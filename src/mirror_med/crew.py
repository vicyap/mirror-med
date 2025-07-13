import asyncio
import json
from typing import Any, Dict, Tuple

from crewai import LLM, Agent, Crew, Process, Task
from crewai.task import TaskOutput

from mirror_med.logging import get_logger


def validate_specialist_output(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate specialist task output contains recommendation."""
    return (True, str(result)) if len(str(result)) > 20 else (False, "Output too short")


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
    agent_llm = LLM(
        model="openai/gpt-4.1-nano", temperature=0.4
    )  # OpenAI's latest and fastest model (released April 2025)

    # Primary Care Physician Manager
    return Agent(
        role="Primary Care Physician Manager",
        goal="Coordinate comprehensive patient health assessment, delegate supplement recommendations to the nutritionist, and compile all findings into a complete JSON response",
        backstory="Board-certified physician manager coordinating health assessments by delegating to specialists and compiling results.",
        tools=[],
        verbose=True,
        allow_delegation=True,
        max_iter=10,
        max_rpm=None,
        cache=True,
        llm=agent_llm,
    )


def create_compiler_agent() -> Agent:
    """Create and return the results compiler agent."""
    # Configure LLM for the agent
    agent_llm = LLM(
        model="openai/gpt-4.1-nano", temperature=0.4
    )  # OpenAI's latest and fastest model (released April 2025)

    # Results Compiler Agent
    return Agent(
        role="Health Assessment Compiler",
        goal="Compile all health recommendations from specialists into a complete JSON response",
        backstory="Medical data specialist who compiles health assessments into structured JSON reports.",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_rpm=None,
        max_iter=5,
        cache=True,
        llm=agent_llm,
    )


def create_alcohol_specialist_agent() -> Agent:
    """Create and return the alcohol consumption specialist agent."""
    # Configure LLM for the agent
    agent_llm = LLM(
        model="openai/gpt-4.1-nano", temperature=0.4
    )  # OpenAI's latest and fastest model (released April 2025)

    return Agent(
        role="Alcohol Consumption Specialist",
        goal="Analyze patient alcohol consumption patterns and provide evidence-based recommendations for optimization",
        backstory="Certified addiction counselor specializing in alcohol consumption patterns and harm reduction strategies.",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_rpm=None,
        max_iter=5,
        cache=True,
        llm=agent_llm,
    )


def create_sleep_specialist_agent() -> Agent:
    """Create and return the sleep quality specialist agent."""
    # Configure LLM for the agent
    agent_llm = LLM(
        model="openai/gpt-4.1-nano", temperature=0.4
    )  # OpenAI's latest and fastest model (released April 2025)

    return Agent(
        role="Sleep Quality Specialist",
        goal="Evaluate patient sleep patterns and provide evidence-based recommendations for sleep optimization",
        backstory="Board-certified sleep medicine specialist with 12+ years experience in sleep optimization and behavioral interventions.",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_rpm=None,
        max_iter=5,
        cache=True,
        llm=agent_llm,
    )


def create_exercise_specialist_agent() -> Agent:
    """Create and return the exercise and physical activity specialist agent."""
    # Configure LLM for the agent
    agent_llm = LLM(
        model="openai/gpt-4.1-nano", temperature=0.4
    )  # OpenAI's latest and fastest model (released April 2025)

    return Agent(
        role="Exercise and Physical Activity Specialist",
        goal="Assess patient exercise habits and provide personalized recommendations for physical activity optimization",
        backstory="Certified exercise physiologist specializing in personalized fitness programs for various health conditions.",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_rpm=None,
        max_iter=5,
        cache=True,
        llm=agent_llm,
    )


def create_nutritionist_agent() -> Agent:
    """Create and return the clinical nutritionist agent."""
    # Configure LLM for the agent
    agent_llm = LLM(
        model="openai/gpt-4.1-nano", temperature=0.4
    )  # OpenAI's latest and fastest model (released April 2025)

    # Clinical Nutritionist
    return Agent(
        role="Nutritionist",
        goal="Analyze patient data and provide evidence-based nutritional supplement recommendations",
        backstory="Registered dietitian with 15+ years expertise in evidence-based supplementation and nutritional biochemistry.",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_rpm=None,
        max_iter=5,
        cache=True,
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
    4. Nutritional supplements - IMPORTANT: You MUST delegate this to the 'nutritionist' 
       coworker for evidence-based supplement recommendations. Ask the nutritionist to provide 
       specific supplements with dosages considering the patient's medications, conditions, and health goals.
    
    WORKFLOW:
    1. First, delegate to the 'nutritionist' to get supplement recommendations
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
    Provide 2-3 evidence-based supplement recommendations. For each:
    - Name, form, dosage (e.g., "Vitamin D3 2000 IU daily")
    - Expected benefits for this patient
    - Any important interactions or timing considerations
    """

    return Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
        async_execution=True,  # Enable async execution
        guardrail=validate_specialist_output,
        max_retries=3,
    )


def create_alcohol_task(agent: Agent) -> Task:
    """
    Create the alcohol consumption assessment task.

    Args:
        agent: The alcohol specialist agent to assign the task to

    Returns:
        Task: The configured alcohol assessment task
    """
    task_description = """
    As the Alcohol Consumption Specialist, analyze the patient's alcohol consumption patterns and provide 
    evidence-based recommendations based on:
    
    PATIENT INFORMATION:
    - Current Alcohol Consumption: {alcohol_description} (current rating: {alcohol_rating}/10)
    - Medical History: {medical_conditions}
    - Current Medications: {medications}
    - Family History: Father - {family_history_father}, Mother - {family_history_mother}
    
    - Vital Signs & Measurements:
      * Blood Pressure: {blood_pressure}
      * Cholesterol: Total {cholesterol_total}, HDL {cholesterol_hdl}, LDL {cholesterol_ldl}
    
    - Health Risks:
      * Cardiovascular risk (10-year): {cardiovascular_risk}
      * Dementia risk: {dementia_risk}
    
    Provide specific recommendations that:
    1. Consider interactions with current medications
    2. Address cardiovascular and dementia risk factors
    3. Suggest practical harm reduction strategies if needed
    4. Provide a rating (1-10) for the potential benefit of following your recommendations
    """

    expected_output = """
    Provide alcohol consumption recommendations:
    - Specific recommendation with limits (e.g., drinks per week)
    - Key health benefits of following this recommendation
    - Rating (1-10) for potential health improvement
    """

    return Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
        async_execution=True,  # Enable async execution
        guardrail=validate_specialist_output,
        max_retries=3,
    )


def create_sleep_task(agent: Agent) -> Task:
    """
    Create the sleep quality assessment task.

    Args:
        agent: The sleep specialist agent to assign the task to

    Returns:
        Task: The configured sleep assessment task
    """
    task_description = """
    As the Sleep Quality Specialist, evaluate the patient's sleep patterns and provide 
    evidence-based recommendations based on:
    
    PATIENT INFORMATION:
    - Current Sleep Pattern: {sleep_description} (current rating: {sleep_rating}/10)
    - Occupation: {occupation}
    - Medical History: {medical_conditions}
    - Current Medications: {medications}
    
    - Vital Signs & Measurements:
      * Weight: {weight} lbs, Height: {height} inches
      * Blood Pressure: {blood_pressure}
    
    - Health Risks:
      * Cardiovascular risk (10-year): {cardiovascular_risk}
      * Metabolic disease risk: {metabolic_risk}
      * Dementia risk: {dementia_risk}
    
    Provide specific recommendations that:
    1. Address sleep quality and duration issues
    2. Consider work schedule and lifestyle factors
    3. Suggest sleep hygiene improvements
    4. Account for any medication effects on sleep
    5. Provide a rating (1-10) for the potential benefit of following your recommendations
    """

    expected_output = """
    Provide sleep optimization recommendations:
    - Specific sleep schedule and duration target
    - Key sleep hygiene practices to implement
    - Rating (1-10) for potential health improvement
    """

    return Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
        async_execution=True,  # Enable async execution
        guardrail=validate_specialist_output,
        max_retries=3,
    )


def create_exercise_task(agent: Agent) -> Task:
    """
    Create the exercise and physical activity assessment task.

    Args:
        agent: The exercise specialist agent to assign the task to

    Returns:
        Task: The configured exercise assessment task
    """
    task_description = """
    As the Exercise and Physical Activity Specialist, assess the patient's exercise habits and provide 
    personalized recommendations based on:
    
    PATIENT INFORMATION:
    - Current Exercise Pattern: {exercise_description} (current rating: {exercise_rating}/10)
    - Occupation: {occupation}
    - Medical History: {medical_conditions}
    - Current Medications: {medications}
    
    - Vital Signs & Measurements:
      * Weight: {weight} lbs, Height: {height} inches
      * Blood Pressure: {blood_pressure}
      * Cholesterol: Total {cholesterol_total}, HDL {cholesterol_hdl}, LDL {cholesterol_ldl}
    
    - Health Risks:
      * Cardiovascular risk (10-year): {cardiovascular_risk}
      * Metabolic disease risk: {metabolic_risk}
    
    Provide specific recommendations that:
    1. Build on current activity level progressively
    2. Address cardiovascular and metabolic risk factors
    3. Consider any physical limitations or medical conditions
    4. Balance cardio, strength, and flexibility training
    5. Provide a rating (1-10) for the potential benefit of following your recommendations
    """

    expected_output = """
    Provide exercise recommendations:
    - Weekly exercise plan (days, duration, intensity)
    - Specific activities recommended
    - Rating (1-10) for potential health improvement
    """

    return Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
        async_execution=True,  # Enable async execution
        guardrail=validate_specialist_output,
        max_retries=3,
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
    Compile all the health recommendations that have been provided by the specialist agents into a final JSON response.
    
    You should have received recommendations from:
    1. Alcohol Consumption Specialist - alcohol optimization recommendations
    2. Sleep Quality Specialist - sleep improvement recommendations
    3. Exercise Specialist - physical activity recommendations
    4. Nutritionist - nutritional supplement recommendations
    
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
    Create the sequential crew for parallel patient health assessment.

    Returns:
        Crew: The configured sequential crew with async tasks
    """
    # Create all specialist agents
    alcohol_specialist = create_alcohol_specialist_agent()
    sleep_specialist = create_sleep_specialist_agent()
    exercise_specialist = create_exercise_specialist_agent()
    nutritionist = create_nutritionist_agent()
    compiler = create_compiler_agent()

    # Create async tasks for parallel execution
    alcohol_task = create_alcohol_task(alcohol_specialist)
    sleep_task = create_sleep_task(sleep_specialist)
    exercise_task = create_exercise_task(exercise_specialist)
    supplements_task = create_supplements_task(nutritionist)

    # Create compilation task with context from all async tasks
    compilation_task = create_compilation_task(compiler)
    compilation_task.context = [
        alcohol_task,
        sleep_task,
        exercise_task,
        supplements_task,
    ]

    # Use sequential process to enable parallel async execution
    return Crew(
        agents=[
            alcohol_specialist,
            sleep_specialist,
            exercise_specialist,
            nutritionist,
            compiler,
        ],
        tasks=[
            alcohol_task,
            sleep_task,
            exercise_task,
            supplements_task,
            compilation_task,
        ],
        process=Process.sequential,  # Sequential process for async tasks
        verbose=True,  # Enable verbose to see task execution
        max_rpm=None,  # No rate limiting
    )


async def run_patient_health_assessment_async(
    patient_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run the patient health assessment crew asynchronously.

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
        logger.info("Starting async patient health assessment")
        # Use kickoff_async for non-blocking execution
        result = await crew.kickoff_async(inputs)

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
        logger.error("Error during async assessment", error=str(e))
        raise


def run_patient_health_assessment(
    patient_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run the patient health assessment crew (synchronous wrapper).

    Args:
        patient_data: Patient data dictionary

    Returns:
        Dict containing health recommendations
    """
    # Run the async version using asyncio.run()
    return asyncio.run(run_patient_health_assessment_async(patient_data))
