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


def _create_pcp_agent() -> Agent:
    """Create and return the PCP agent."""
    # Configure LLM for the agent
    agent_llm = LLM(model="openai/gpt-4.1-nano")

    # Primary Care Physician
    return Agent(
        role="Primary Care Physician",
        goal="Analyze patient health data and create personalized health improvement recommendations",
        backstory="""You are a board-certified Internal Medicine physician with 20 years 
        of experience in primary care and preventive medicine. You excel at analyzing 
        patient data to create holistic health plans. You follow evidence-based guidelines 
        from the ACP, AAFP, and USPSTF. You have expertise in lifestyle medicine, preventive 
        care, nutrition, sleep medicine, and exercise physiology. You provide comprehensive 
        recommendations for alcohol consumption, sleep optimization, exercise routines, and 
        nutritional supplements based on the patient's current health status and risk factors.""",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_iter=25,
        max_rpm=None,
        llm=agent_llm,
    )


def create_health_assessment_task(agent: Agent) -> Task:
    """
    Create the comprehensive health assessment task.

    Args:
        agent: The agent to assign the task to

    Returns:
        Task: The configured health assessment task
    """
    task_description = """
    Conduct a comprehensive health assessment for a patient visit with the following data:
    
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
    
    As the Primary Care Physician, analyze this patient data and provide comprehensive health improvement recommendations.
    
    You should assess and provide specific recommendations for:
    
    1. Alcohol consumption - Evaluate current intake and provide optimization recommendations
    2. Sleep patterns - Analyze sleep quality/duration and suggest improvements
    3. Exercise routine - Evaluate current activity and recommend enhancements
    4. Nutritional supplements - Recommend evidence-based supplements based on patient's health status
    
    Additionally, provide an UPDATED HEALTH FORECAST showing the expected improvements if the patient follows all your recommendations. Be realistic but optimistic about the potential health improvements.
    
    Consider the patient's risk factors, current medications, and health forecast when making recommendations.
    Provide practical, actionable advice that the patient can implement.
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
    
    Ensure all ratings are integers between 1-10. Include at least 1-2 supplement recommendations.
    The forecast should show realistic improvements based on following the recommendations.
    """

    return Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
    )


def create_crew() -> Crew:
    """
    Create the sequential crew for patient health assessment.

    Returns:
        Crew: The configured sequential crew
    """
    # Create the agent
    pcp = _create_pcp_agent()

    # Create the task
    health_assessment_task = create_health_assessment_task(pcp)

    # Create and return the crew
    return Crew(
        agents=[pcp],
        tasks=[health_assessment_task],
        process=Process.sequential,  # Sequential process for single agent
        verbose=False,
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
