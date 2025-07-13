import json
from typing import Any, Dict

from crewai import LLM, Agent, Crew, Process, Task

from mirror_med.logging import get_logger


def flatten_patient_data(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten nested patient data into a flat dictionary for crew inputs.

    Args:
        patient_data: Nested patient data dictionary

    Returns:
        Flattened dictionary suitable for crew.kickoff(inputs)
    """
    inputs = {
        # Social History
        "diet": patient_data["social_history"]["food"],
        "exercise_description": patient_data["social_history"]["exercise"][
            "description"
        ],
        "exercise_rating": patient_data["social_history"]["exercise"]["rating"],
        "alcohol_description": patient_data["social_history"]["alcohol"]["description"],
        "alcohol_rating": patient_data["social_history"]["alcohol"]["rating"],
        "sleep_description": patient_data["social_history"]["sleep"]["description"],
        "sleep_rating": patient_data["social_history"]["sleep"]["rating"],
        "occupation": patient_data["social_history"]["occupation"],
        # Medical History
        "medical_conditions": ", ".join(patient_data["medical_history"]["conditions"]),
        # Medications
        "medications": ", ".join(
            [f"{med['name']} {med['dose']}" for med in patient_data["medications"]]
        ),
        # Allergies
        "allergies": ", ".join(
            [
                f"{allergy['allergen']} ({allergy['reaction']})"
                for allergy in patient_data["allergies"]
            ]
        ),
        # Family History
        "family_history_father": ", ".join(patient_data["family_history"]["father"]),
        "family_history_mother": ", ".join(patient_data["family_history"]["mother"]),
        # Measurements
        "weight": patient_data["measurements"]["weight"],
        "height": patient_data["measurements"]["height"],
        "blood_pressure": patient_data["measurements"]["blood_pressure"],
        "cholesterol_total": patient_data["measurements"]["cholesterol"],
        "cholesterol_hdl": patient_data["measurements"]["hdl"],
        "cholesterol_ldl": patient_data["measurements"]["ldl"],
        "triglycerides": patient_data["measurements"]["triglycerides"],
        # Health Forecast
        "cardiovascular_risk": patient_data["forecast"][
            "cardiovascular_event_10yr_probability"
        ],
        "dementia_risk": patient_data["forecast"]["dementia_risk"],
        "metabolic_risk": patient_data["forecast"]["metabolic_disease_risk"],
    }
    return inputs


def create_pcp_manager_agent() -> Agent:
    """Create and return the PCP manager agent."""
    # Configure LLM for the agent
    agent_llm = LLM(model="openai/gpt-4.1-nano")

    # Primary Care Physician Manager
    return Agent(
        role="Primary Care Physician Manager",
        goal="Coordinate comprehensive patient health assessment, delegate supplement recommendations to the nutritionist, and compile all findings into a complete JSON response",
        backstory="""You are a board-certified Internal Medicine physician with 20 years 
        of experience in primary care and preventive medicine. As the lead physician manager, you excel 
        at coordinating comprehensive health assessments by delegating to specialist colleagues. 
        
        Your workflow:
        1. Analyze patient data for alcohol, sleep, and exercise recommendations
        2. DELEGATE supplement recommendations to the 'clinical nutritionist' (use this exact name)
        3. Receive and incorporate the nutritionist's supplement recommendations
        4. Compile ALL recommendations into a single, complete JSON response
        
        You MUST produce a final JSON output that includes recommendations for alcohol, sleep, 
        exercise, AND the nutritionist's supplement recommendations, plus an updated health forecast.
        Never end your work with a delegation action - always compile the final JSON response.""",
        tools=[],
        verbose=True,
        allow_delegation=True,
        max_iter=50,
        max_rpm=None,
        llm=agent_llm,
    )


def create_compiler_agent() -> Agent:
    """Create and return the results compiler agent."""
    # Configure LLM for the agent
    agent_llm = LLM(model="openai/gpt-4.1-nano")

    # Results Compiler Agent
    return Agent(
        role="Health Assessment Compiler",
        goal="Compile all health recommendations from specialists into a complete JSON response",
        backstory="""You are a medical data specialist who excels at compiling comprehensive 
        health assessments. Your role is to gather all recommendations from the team (alcohol, 
        sleep, exercise, and supplements) and format them into the required JSON structure.
        
        You ensure that:
        1. All recommendations are included with proper ratings (1-10)
        2. The health forecast is updated based on the recommendations
        3. The output is valid JSON with no additional text
        
        You work at the end of the assessment process to compile the final report.""",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_rpm=None,
        llm=agent_llm,
    )


def create_nutritionist_agent() -> Agent:
    """Create and return the clinical nutritionist agent."""
    # Configure LLM for the agent
    agent_llm = LLM(model="openai/gpt-4.1-nano")

    # Clinical Nutritionist
    return Agent(
        role="Clinical Nutritionist",
        goal="Analyze patient data and provide evidence-based nutritional supplement recommendations",
        backstory="""You are a registered dietitian and clinical nutritionist with expertise 
        in nutritional biochemistry and supplementation protocols. You have 15 years of experience 
        in personalized nutrition and evidence-based supplementation. You excel at analyzing 
        patient health data, medications, and conditions to recommend appropriate nutritional 
        supplements. You understand drug-nutrient interactions, bioavailability, dosing protocols, 
        and quality standards for supplements. You follow guidelines from the Academy of Nutrition 
        and Dietetics, and stay current with nutritional research. You provide specific supplement 
        recommendations with dosages and expected benefits based on individual patient needs, 
        always prioritizing safety and efficacy.""",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_rpm=None,
        llm=agent_llm,
    )


def create_health_assessment_task(agent: Agent) -> Task:
    """
    Create the comprehensive health assessment task for the PCP manager.

    Args:
        agent: The agent to assign the task to

    Returns:
        Task: The configured health assessment task
    """
    task_description = """
    As the Primary Care Physician Manager, coordinate a comprehensive health assessment for a patient visit with the following data:
    
    PATIENT INFORMATION:
    - Social History:
      * Diet: {diet}
      * Exercise: {exercise_description} (current rating: {exercise_rating}/10)
      * Alcohol: {alcohol_description} (current rating: {alcohol_rating}/10)
      * Sleep: {sleep_description} (current rating: {sleep_rating}/10)
      * Occupation: {occupation}
    
    - Medical History: {medical_conditions}
    - Current Medications: {medications}
    - Allergies: {allergies}
    - Family History: Father - {family_history_father}, Mother - {family_history_mother}
    
    - Vital Signs & Measurements:
      * Weight: {weight} lbs
      * Height: {height} inches
      * Blood Pressure: {blood_pressure}
      * Cholesterol: Total {cholesterol_total}, HDL {cholesterol_hdl}, LDL {cholesterol_ldl}
      * Triglycerides: {triglycerides}
    
    - Health Forecast:
      * Cardiovascular risk (10-year): {cardiovascular_risk}
      * Dementia risk: {dementia_risk}
      * Metabolic disease risk: {metabolic_risk}
    
    You need to coordinate the team to provide comprehensive health improvement recommendations for:
    
    1. Alcohol consumption - Evaluate current intake and provide optimization recommendations
    2. Sleep patterns - Analyze sleep quality/duration and suggest improvements
    3. Exercise routine - Evaluate current activity and recommend enhancements
    4. Nutritional supplements - IMPORTANT: You MUST delegate this to the 'clinical nutritionist' 
       (use lowercase) for evidence-based supplement recommendations. Ask the nutritionist to provide 
       specific supplements with dosages considering the patient's medications, conditions, and health goals.
    
    WORKFLOW:
    1. First, delegate to the 'clinical nutritionist' to get supplement recommendations
    2. Once you receive the nutritionist's recommendations, incorporate them into your assessment
    3. Compile all recommendations (alcohol, sleep, exercise, AND the nutritionist's supplements)
    4. Calculate an updated health forecast based on all recommendations
    
    CRITICAL: After delegating and receiving the nutritionist's input, you MUST compile everything into 
    a single JSON response. Do not end with a delegation action. Your final answer must be the complete 
    JSON response as specified in the expected output format below.
    """

    expected_output = """
    IMPORTANT: Provide your response ONLY as valid JSON with no additional text or markdown formatting.
    
    Return a comprehensive health improvement plan with updated forecast in exactly this JSON format:
    {
        "recommendations": {
            "alcohol": {
                "description": "Specific recommendation for alcohol consumption",
                "rating": <integer 1-10 indicating future benefit>
            },
            "sleep": {
                "description": "Specific recommendation for sleep improvement", 
                "rating": <integer 1-10 indicating future benefit>
            },
            "exercise": {
                "description": "Specific recommendation for exercise routine",
                "rating": <integer 1-10 indicating future benefit>
            },
            "supplements": [
                {
                    "description": "Specific supplement recommendation with dosage",
                    "rating": <integer 1-10 indicating future benefit>
                }
            ]
        },
        "forecast": {
            "life_expectancy_years": <float showing improved life expectancy>,
            "cardiovascular_event_10yr_probability": <float between 0-1 showing reduced risk>,
            "energy_level": <"Low", "Moderate", or "High">,
            "metabolic_disease_risk": <"Low", "Moderate", or "High">,
            "dementia_risk": <"Low", "Moderate", or "High">,
            "last_updated": <current date as "YYYY-MM-DD">
        }
    }
    
    Ensure all ratings are integers between 1-10. Include at least 1-2 supplement recommendations from the nutritionist.
    The forecast should show realistic improvements based on following the recommendations.
    """

    return Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
    )


def create_supplements_task(agent: Agent) -> Task:
    """
    Create the nutritional supplements recommendation task.

    Args:
        agent: The nutritionist agent to assign the task to

    Returns:
        Task: The configured supplements task
    """
    task_description = """
    As the Clinical Nutritionist, analyze the patient data and provide evidence-based nutritional supplement 
    recommendations based on:
    
    PATIENT INFORMATION:
    - Diet: {diet}
    - Medical History: {medical_conditions}
    - Current Medications: {medications}
    - Allergies: {allergies}
    - Family History: Father - {family_history_father}, Mother - {family_history_mother}
    
    - Vital Signs & Measurements:
      * Weight: {weight} lbs, Height: {height} inches
      * Cholesterol: Total {cholesterol_total}, HDL {cholesterol_hdl}, LDL {cholesterol_ldl}
      * Triglycerides: {triglycerides}
    
    - Health Risks:
      * Cardiovascular risk (10-year): {cardiovascular_risk}
      * Dementia risk: {dementia_risk}
      * Metabolic disease risk: {metabolic_risk}
    
    Provide specific, evidence-based supplement recommendations that:
    1. Address the patient's health conditions and risk factors
    2. Consider potential drug-nutrient interactions with current medications
    3. Include specific dosages, forms, and timing
    4. Explain the expected benefits based on the patient's health profile
    
    Focus on supplements that have strong scientific evidence for this patient's specific needs.
    """

    expected_output = """
    Provide a detailed list of nutritional supplement recommendations in the following format:
    
    For each recommended supplement:
    - Name and specific form (e.g., "Vitamin D3 (cholecalciferol)")
    - Dosage and frequency (e.g., "2000 IU daily")
    - Best time to take and any special instructions
    - Expected benefits specific to this patient
    - Any interactions or precautions to consider
    - Quality indicators to look for when purchasing
    
    Prioritize supplements with the strongest evidence for this patient's conditions and risk factors.
    Include at least 2-3 well-justified recommendations.
    """

    return Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
    )


def create_compilation_task(agent: Agent) -> Task:
    """
    Create the final compilation task.

    Args:
        agent: The compiler agent to assign the task to

    Returns:
        Task: The configured compilation task
    """
    task_description = """
    Compile all the health recommendations that have been provided by the team into a final JSON response.
    
    You should have received or have access to:
    1. Alcohol consumption recommendations from the PCP
    2. Sleep pattern recommendations from the PCP
    3. Exercise routine recommendations from the PCP
    4. Nutritional supplement recommendations from the Clinical Nutritionist
    
    Take all these recommendations and compile them into the required JSON format.
    Include an updated health forecast showing realistic improvements based on following all recommendations.
    
    IMPORTANT: Your output must be ONLY the JSON response with no additional text or explanation.
    """

    expected_output = """
    Return ONLY this JSON structure with no additional text:
    {
        "recommendations": {
            "alcohol": {
                "description": "Specific recommendation for alcohol consumption",
                "rating": <integer 1-10 indicating future benefit>
            },
            "sleep": {
                "description": "Specific recommendation for sleep improvement", 
                "rating": <integer 1-10 indicating future benefit>
            },
            "exercise": {
                "description": "Specific recommendation for exercise routine",
                "rating": <integer 1-10 indicating future benefit>
            },
            "supplements": [
                {
                    "description": "Specific supplement recommendation with dosage",
                    "rating": <integer 1-10 indicating future benefit>
                }
            ]
        },
        "forecast": {
            "life_expectancy_years": <float showing improved life expectancy>,
            "cardiovascular_event_10yr_probability": <float between 0-1 showing reduced risk>,
            "energy_level": <"Low", "Moderate", or "High">,
            "metabolic_disease_risk": <"Low", "Moderate", or "High">,
            "dementia_risk": <"Low", "Moderate", or "High">,
            "last_updated": <current date as "YYYY-MM-DD">
        }
    }
    """

    return Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
    )


def create_crew() -> Crew:
    """
    Create the hierarchical crew for patient health assessment.

    Returns:
        Crew: The configured hierarchical crew
    """
    # Create the agents
    pcp = create_pcp_manager_agent()
    nutritionist = create_nutritionist_agent()
    compiler = create_compiler_agent()

    # Create the tasks
    health_assessment_task = create_health_assessment_task(pcp)
    supplements_task = create_supplements_task(nutritionist)

    # Create compilation task with context from previous tasks
    compilation_task = create_compilation_task(compiler)
    compilation_task.context = [health_assessment_task, supplements_task]

    # Use hierarchical process with the PCP as a custom manager agent
    # The manager will coordinate tasks and the compiler will produce final output
    return Crew(
        agents=[nutritionist, compiler],  # Specialist agents
        tasks=[health_assessment_task, supplements_task, compilation_task],
        manager_agent=pcp,  # PCP acts as the manager
        process=Process.hierarchical,  # Hierarchical process
        verbose=True,  # Enable verbose to see delegation
        max_rpm=None,  # No rate limiting
    )


def run_patient_health_assessment(
    patient_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run the patient health assessment crew.

    Args:
        patient_data: Patient data dictionary

    Returns:
        Dict containing health recommendations
    """
    # Get logger
    logger = get_logger(__name__)

    # Create the crew
    crew = create_crew()

    # Flatten patient data into inputs
    inputs = flatten_patient_data(patient_data)

    try:
        logger.info("Starting patient health assessment")
        result = crew.kickoff(inputs)

        # Try to parse the result as JSON
        try:
            # Extract JSON from the result if it's embedded in text
            import re

            json_match = re.search(r"\{[\s\S]*\}", str(result))
            if json_match:
                crew_output = json.loads(json_match.group())
                logger.info(
                    "Successfully parsed crew output",
                    has_recommendations="recommendations" in crew_output,
                    has_forecast="forecast" in crew_output,
                )
                return crew_output
            else:
                logger.warning(
                    "Could not extract JSON from result, returning raw output"
                )
                return {"raw_output": str(result)}
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from result, returning raw output")
            return {"raw_output": str(result)}

    except Exception as e:
        logger.error("Error during assessment", error=str(e))
        raise
