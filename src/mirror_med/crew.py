import json
from typing import Any, Dict, Tuple

from crewai import LLM, Agent, Crew, Process, Task
from crewai.task import TaskOutput
from crewai_tools import EXASearchTool

from mirror_med.logging import get_logger

# LLM Configuration Constants
AGENT_LLM_MODEL = (
    "openai/gpt-4.1-nano"  # OpenAI's latest and fastest model (released April 2025)
)
AGENT_LLM_TEMPERATURE = 0.5


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
        "life_expectancy": patient_data["forecast"]["life_expectancy_years"],
        "cardiovascular_risk": patient_data["forecast"][
            "cardiovascular_event_10yr_probability"
        ],
        "energy_level": patient_data["forecast"]["energy_level"],
        "dementia_risk": patient_data["forecast"]["dementia_risk"],
        "metabolic_risk": patient_data["forecast"]["metabolic_disease_risk"],
    }
    return inputs


def create_pcp_manager_agent() -> Agent:
    """Create and return the PCP manager agent."""
    # Configure LLM for the agent
    agent_llm = LLM(model=AGENT_LLM_MODEL, temperature=AGENT_LLM_TEMPERATURE)

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
    agent_llm = LLM(model=AGENT_LLM_MODEL, temperature=AGENT_LLM_TEMPERATURE)

    # Results Compiler Agent
    return Agent(
        role="Health Assessment Compiler",
        goal="Compile recommendations ensuring maximum positive impact on life expectancy, cardiovascular risk reduction, and energy optimization",
        backstory="Health optimization specialist who ensures all recommendations synergistically improve the health forecast metrics.",
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
    agent_llm = LLM(model=AGENT_LLM_MODEL, temperature=AGENT_LLM_TEMPERATURE)

    # Initialize the EXA search tool for evidence-based research
    exa_tool = EXASearchTool()

    return Agent(
        role="Alcohol Consumption Specialist",
        goal="Maximize life expectancy and minimize cardiovascular/dementia risk through evidence-based alcohol REDUCTION strategies",
        backstory="Longevity-focused addiction counselor specializing in reducing mortality risk by helping patients LOWER alcohol consumption to improve cardiovascular health and brain function.",
        tools=[exa_tool],
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
    agent_llm = LLM(model=AGENT_LLM_MODEL, temperature=AGENT_LLM_TEMPERATURE)

    # Initialize the EXA search tool for evidence-based research
    exa_tool = EXASearchTool()

    return Agent(
        role="Sleep Quality Specialist",
        goal="Dramatically improve energy levels and reduce metabolic/dementia risk through sleep optimization for maximum health forecast gains",
        backstory="Sleep medicine specialist focused on longevity, using sleep as a powerful tool to reduce cardiovascular events, metabolic disease, and cognitive decline.",
        tools=[exa_tool],
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
    agent_llm = LLM(model=AGENT_LLM_MODEL, temperature=AGENT_LLM_TEMPERATURE)

    # Initialize the EXA search tool for evidence-based research
    exa_tool = EXASearchTool()

    return Agent(
        role="Exercise and Physical Activity Specialist",
        goal="Design exercise programs that maximally reduce cardiovascular risk and increase life expectancy through evidence-based physical activity",
        backstory="Exercise physiologist specializing in longevity protocols proven to reduce 10-year cardiovascular risk and extend healthy lifespan.",
        tools=[exa_tool],
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
    agent_llm = LLM(model=AGENT_LLM_MODEL, temperature=AGENT_LLM_TEMPERATURE)

    # Initialize the EXA search tool for evidence-based research
    exa_tool = EXASearchTool()

    # Clinical Nutritionist
    return Agent(
        role="Nutritionist",
        goal="Recommend targeted supplements to significantly improve cardiovascular markers, metabolic health, and cognitive protection for maximum life extension",
        backstory="Longevity nutritionist using evidence-based supplementation to reduce disease risk and optimize biomarkers for extended healthspan.",
        tools=[exa_tool],
        verbose=True,
        allow_delegation=False,
        max_rpm=None,
        max_iter=5,
        cache=True,
        llm=agent_llm,
    )


def create_single_pcp_agent() -> Agent:
    """Create and return a single comprehensive PCP agent that handles all assessments."""
    # Configure LLM for the agent
    agent_llm = LLM(model=AGENT_LLM_MODEL, temperature=AGENT_LLM_TEMPERATURE)

    # Initialize the EXA search tool for quick evidence-based medical research
    exa_tool = EXASearchTool()

    # Primary Care Physician
    return Agent(
        role="Primary Care Physician",
        goal="Provide complete health assessment including alcohol optimization, sleep improvement, exercise recommendations, and targeted supplement suggestions to maximize life expectancy and minimize disease risk",
        backstory="Board-certified physician with 20+ years experience in preventive medicine, nutrition, sleep medicine, and exercise physiology. Expert at creating integrated health plans that synergistically improve all health metrics for maximum longevity gains.",
        tools=[exa_tool],
        verbose=True,
        allow_delegation=False,
        max_rpm=None,
        max_iter=10,
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
    
    1. Alcohol consumption - Evaluate current intake and provide recommendations to REDUCE consumption for health benefits
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
                "description": "Specific recommendation to reduce alcohol consumption",
                "rating": <integer 1-10 indicating health benefit of following this recommendation>
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
    ⚠️ MANDATORY TOOL USAGE REQUIREMENT ⚠️
    You MUST use the EXA search tool for ALL supplement recommendations. General knowledge is NOT acceptable.
    ❌ DO NOT provide any recommendation without first searching for current evidence
    ✅ Search for: "heart disease supplements evidence", "vitamin D cardiovascular benefits 2024", etc.
    
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
    
    📝 SEARCH PROCESS:
    1. Search EXA for supplements proven effective for this patient's conditions
    2. Search for specific dosing and safety data
    3. Extract URLs from your search results
    4. Base ALL recommendations on evidence found
    
    ⚠️ CRITICAL OUTPUT FORMAT REQUIREMENT ⚠️
    Your supplement descriptions MUST be:
    - MAXIMUM 80 characters per recommendation
    - Simple format: "Supplement name dosage frequency"
    - NO explanations, NO justifications, NO context
    
    ✅ GOOD Examples (under 80 chars):
    - "Omega-3 1000mg daily"
    - "Vitamin D3 2000 IU daily" 
    - "Magnesium glycinate 400mg at bedtime"
    - "CoQ10 100mg twice daily"
    
    ❌ BAD Examples (too long/detailed):
    - "High-quality omega-3 fatty acids 1000mg daily for cardiovascular protection"
    - "Vitamin D3 2000 IU daily to improve immune function and bone health"
    
    CHARACTER COUNT REMINDER: Each description MUST be under 80 characters!
    
    CRITICAL: Prioritize supplements with strongest evidence for health forecast improvements:
    - Life expectancy extension through targeted supplementation
    - Cardiovascular protection (omega-3, CoQ10 if indicated)
    - Metabolic support (vitamin D, magnesium)
    - Cognitive protection (B-complex, antioxidants)
    - Higher ratings (9-10) for supplements with proven longevity benefits
    """

    expected_output = """
    IMPORTANT: Provide your response ONLY as valid JSON with no additional text or markdown formatting.
    
    Return your recommendations in exactly this JSON format:
    {
        "evidence_urls": ["https://url1.com", "https://url2.com", "https://url3.com"],
        "recommendations": [
            {
                "description": "Omega-3 1000mg daily",
                "rating": <integer 1-10 indicating future benefit>,
                "evidence_based": true
            },
            {
                "description": "Vitamin D3 2000 IU daily",
                "rating": <integer 1-10 indicating future benefit>,
                "evidence_based": true
            }
        ]
    }
    
    FINAL REMINDER: Each description MUST be under 80 characters!
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
    ⚠️ MANDATORY TOOL USAGE REQUIREMENT ⚠️
    You MUST use the EXA search tool for your recommendation. General knowledge is NOT acceptable.
    ❌ DO NOT provide any recommendation without first searching for current evidence
    ✅ ALWAYS search for alcohol consumption guidelines based on patient specifics
    
    As the Alcohol Consumption Specialist, analyze the patient's alcohol consumption patterns and provide 
    evidence-based recommendations based on:
    
    PATIENT INFORMATION:
    - Current Alcohol Consumption: {alcohol_description} (current rating: {alcohol_rating}/10 - Note: Higher rating = worse for health)
    - Medical History: {medical_conditions}
    - Current Medications: {medications}
    - Family History: Father - {family_history_father}, Mother - {family_history_mother}
    
    - Vital Signs & Measurements:
      * Blood Pressure: {blood_pressure}
      * Cholesterol: Total {cholesterol_total}, HDL {cholesterol_hdl}, LDL {cholesterol_ldl}
    
    - Health Risks:
      * Cardiovascular risk (10-year): {cardiovascular_risk}
      * Dementia risk: {dementia_risk}
    
    ⚠️ CRITICAL OUTPUT FORMAT REQUIREMENT ⚠️
    Your final recommendation description MUST be:
    - MAXIMUM 80 characters
    - Simple, actionable statement only
    - NO explanations, NO justifications, NO context
    
    ❌ BAD: "Reduce alcohol intake to no more than 1 pint of craft beer on Saturdays, aiming for weekly limit"
    ✅ GOOD: "Limit to 1 drink per week"
    
    📋 SEARCH PROTOCOL:
    Use EXA tool to search for current alcohol guidelines considering:
    * Patient's cardiovascular risk and medications
    * Latest 2024-2025 alcohol consumption evidence
    * Example search: "alcohol limits cardiovascular disease hypertension 2025"
    
    ⚠️ CRITICAL: Extract and save the URLs from your search results!
    
    CRITICAL: Your recommendations should target maximum improvement in health forecast metrics:
    - Life expectancy increase: Aim for +2-5 years through alcohol REDUCTION
    - Cardiovascular risk reduction: Target 20-40% reduction by LOWERING alcohol intake
    - Consider impact on dementia risk and energy levels
    - Higher benefit ratings (9-10) for recommendations that significantly REDUCE alcohol consumption
    """

    expected_output = """
    IMPORTANT: Provide your response ONLY as valid JSON with no additional text or markdown formatting.
    
    Return your recommendation in exactly this JSON format:
    {
        "evidence_urls": ["https://url1.com", "https://url2.com"],
        "recommendation": {
            "description": "Limit to 1 drink per week",
            "rating": <integer 1-10 indicating future benefit>,
            "evidence_based": true
        }
    }
    
    FINAL REMINDER: The description MUST be under 80 characters!
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
    ⚠️ MANDATORY TOOL USAGE REQUIREMENT ⚠️
    You MUST use the EXA search tool for your recommendation. General knowledge is NOT acceptable.
    ❌ DO NOT provide any recommendation without first searching for current evidence
    ✅ ALWAYS search for sleep optimization evidence based on patient specifics
    
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
    
    ⚠️ CRITICAL OUTPUT FORMAT REQUIREMENT ⚠️
    Your final recommendation description MUST be:
    - MAXIMUM 80 characters
    - Simple, actionable statement only
    - NO explanations, NO justifications, NO context
    
    ❌ BAD: "Increase sleep duration to 7-8 hours per night and establish consistent sleep schedule"
    ✅ GOOD: "Sleep 7-8 hours nightly"
    
    📋 SEARCH PROTOCOL:
    Use EXA tool to search for evidence-based sleep optimization:
    * Patient's metabolic and dementia risk factors
    * Latest 2024-2025 sleep research
    * Example search: "sleep optimization metabolic syndrome evidence 2024"
    
    ⚠️ CRITICAL: Extract and save the URLs from your search results!
    
    CRITICAL: Focus on sleep interventions that maximize health forecast improvements:
    - Energy level: Transform from Low/Moderate to High
    - Metabolic disease risk: Reduce from High to Low through better sleep
    - Dementia risk: Significant reduction through sleep quality improvement
    - Target 7-9 hours of quality sleep for optimal longevity
    - Higher ratings (9-10) should indicate transformative improvements
    """

    expected_output = """
    IMPORTANT: Provide your response ONLY as valid JSON with no additional text or markdown formatting.
    
    Return your recommendation in exactly this JSON format:
    {
        "evidence_urls": ["https://url1.com", "https://url2.com"],
        "recommendation": {
            "description": "Sleep 7-8 hours nightly",
            "rating": <integer 1-10 indicating future benefit>,
            "evidence_based": true
        }
    }
    
    FINAL REMINDER: The description MUST be under 80 characters!
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
    ⚠️ MANDATORY TOOL USAGE REQUIREMENT ⚠️
    You MUST use the EXA search tool for your recommendation. General knowledge is NOT acceptable.
    ❌ DO NOT provide any recommendation without first searching for current evidence
    ✅ ALWAYS search for exercise recommendations based on patient specifics
    
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
    
    ⚠️ CRITICAL OUTPUT FORMAT REQUIREMENT ⚠️
    Your final recommendation description MUST be:
    - MAXIMUM 80 characters
    - Simple, actionable statement only
    - NO explanations, NO justifications, NO context
    
    ❌ BAD: "Engage in 150 minutes of moderate cardio weekly plus strength training twice per week"
    ✅ GOOD: "150 min cardio + 2x strength training weekly"
    
    📋 SEARCH PROTOCOL:
    Use EXA tool to search for evidence-based exercise recommendations:
    * Patient's cardiovascular and metabolic risk factors
    * Latest 2024-2025 exercise research
    * Example search: "HIIT strength training cardiovascular risk reduction 2025"
    
    ⚠️ CRITICAL: Extract and save the URLs from your search results!
    
    CRITICAL: Design exercise program for maximum health forecast gains:
    - Cardiovascular risk: Target 30-50% reduction in 10-year probability
    - Life expectancy: Aim for +5-10 years through regular exercise
    - Metabolic disease risk: Reduce to Low through fitness improvements
    - Include both cardio (150min/week) and strength training for optimal results
    - Higher ratings (9-10) should indicate life-changing improvements
    """

    expected_output = """
    IMPORTANT: Provide your response ONLY as valid JSON with no additional text or markdown formatting.
    
    Return your recommendation in exactly this JSON format:
    {
        "evidence_urls": ["https://url1.com", "https://url2.com"],
        "recommendation": {
            "description": "150 min cardio + 2x strength training weekly",
            "rating": <integer 1-10 indicating future benefit>,
            "evidence_based": true
        }
    }
    
    FINAL REMINDER: The description MUST be under 80 characters!
    """

    return Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
        async_execution=True,  # Enable async execution
        guardrail=validate_specialist_output,
        max_retries=3,
    )


def create_single_pcp_task(agent: Agent) -> Task:
    """
    Create a comprehensive health assessment task for the single PCP agent.

    Args:
        agent: The single PCP agent to assign the task to

    Returns:
        Task: The configured comprehensive health assessment task
    """
    task_description = """
    ⚠️ MANDATORY TOOL USAGE REQUIREMENT ⚠️
    You MUST use the EXA search tool for EVERY recommendation. General knowledge is NOT acceptable.
    ❌ DO NOT provide any recommendation without first searching for current evidence
    ✅ ALWAYS search before making any health recommendation
    ❌ DO NOT rely on memory - use the tool for 2024-2025 data
    ✅ REQUIRED: At least 4 searches total (minimum 1 per recommendation category)
    
    As a Comprehensive Primary Care Physician, provide a complete health assessment for this patient with the following data:
    
    PATIENT INFORMATION:
    - Social History:
      * Diet: {diet}
      * Exercise: {exercise_description} (current rating: {exercise_rating}/10)
      * Alcohol: {alcohol_description} (current rating: {alcohol_rating}/10 - Note: Higher rating = worse for health)
      * Sleep: {sleep_description} (current rating: {sleep_rating}/10)
      * Occupation: {occupation}
    
    - Medical History: {medical_conditions}
    - Current Medications: {medications}
    - Allergies: {allergies}
    - Family History: Father - {family_history_father}, Mother - {family_history_mother}
    
    - Vital Signs & Measurements:
      * Weight: {weight} lbs, Height: {height} inches
      * Blood Pressure: {blood_pressure}
      * Cholesterol: Total {cholesterol_total}, HDL {cholesterol_hdl}, LDL {cholesterol_ldl}
      * Triglycerides: {triglycerides}
    
    - Health Forecast:
      * Life expectancy: {life_expectancy} years
      * Cardiovascular risk (10-year): {cardiovascular_risk}
      * Energy level: {energy_level}
      * Dementia risk: {dementia_risk}
      * Metabolic disease risk: {metabolic_risk}
    
    Provide comprehensive health improvement recommendations for ALL of the following areas:

    ⚠️ CRITICAL OUTPUT FORMAT REQUIREMENT ⚠️
    While you should analyze thoroughly, your final recommendation descriptions MUST be:
    - MAXIMUM 80 characters per recommendation
    - Simple, actionable statements only
    - NO explanations, NO justifications, NO context
    
    ❌ BAD (too long): "Reduce alcohol intake to no more than 1 pint of craft beer on Saturdays, aiming for weekly limit of 1 standard drink to lower cardiovascular and dementia risks"
    ✅ GOOD (concise): "Limit to 1 drink per week"
    
    ❌ BAD: "Increase sleep duration to 7-8 hours per night and establish consistent sleep schedule"
    ✅ GOOD: "Sleep 7-8 hours nightly"

    1. ALCOHOL CONSUMPTION:
       - Analyze current intake and interactions with medications
       - Provide specific limits to REDUCE consumption for cardiovascular and dementia risk reduction
       - Aim for life expectancy increase of +2-5 years by LOWERING alcohol intake
       - Target 20-40% reduction in 10-year cardiovascular risk through alcohol REDUCTION
    
    2. SLEEP QUALITY:
       - Evaluate sleep patterns considering occupation and lifestyle
       - Recommend specific sleep schedule and hygiene improvements
       - Target energy level improvement from Low/Moderate to High
       - Aim to reduce metabolic and dementia risk through better sleep
    
    3. EXERCISE ROUTINE:
       - Build on current activity level progressively
       - Balance cardio (150min/week) and strength training
       - Target 30-50% cardiovascular risk reduction
       - Aim for +5-10 years life expectancy gain
    
    4. NUTRITIONAL SUPPLEMENTS:
       - Recommend at least 1 evidence-based supplements with specific dosages
       - Consider drug-nutrient interactions with current medications
       - Focus on cardiovascular protection (omega-3, CoQ10 if indicated)
       - Include metabolic support (vitamin D, magnesium) and cognitive protection
    
    📋 STEP-BY-STEP TOOL USAGE PROTOCOL:
    Step 1: Use EXA tool to search for current alcohol consumption guidelines
    Step 2: Use EXA tool to search for evidence-based sleep optimization
    Step 3: Use EXA tool to search for exercise recommendations
    Step 4: Use EXA tool to search for supplement dosages and interactions
    
    ⚠️ CRITICAL: For EACH search, you MUST extract and save the URLs of the sources found.
    The EXA tool returns search results with URLs - you MUST include these URLs in your response.
    
    Example searches (MANDATORY - adapt these to patient specifics):
    * "alcohol limits cardiovascular disease hypertension 2025"
    * "sleep optimization metabolic syndrome evidence 2024"
    * "HIIT strength training cardiovascular risk reduction 2025"
    * "vitamin D magnesium dosage cardiovascular health 2024"
    
    ✓ VALIDATION CHECKLIST (must complete ALL):
    □ Searched for alcohol guidelines using EXA and extracted URLs
    □ Searched for sleep recommendations using EXA and extracted URLs
    □ Searched for exercise protocols using EXA and extracted URLs
    □ Searched for supplement information using EXA and extracted URLs
    
    If any checkbox is incomplete, GO BACK and use the tool.
    Each recommendation MUST be based on the sources you found.
    You MUST include 1-3 URLs per category in the evidence_urls section.
    
    CRITICAL: Your recommendations must show substantial, realistic improvements:
    - Life expectancy: Increase by 5-10 years from baseline
    - Cardiovascular risk: Reduce by 30-50% from baseline
    - Energy level: Improve to 'High' if currently Low/Moderate
    - Metabolic disease risk: Reduce to 'Low' where possible
    - Dementia risk: Reduce to 'Low' where possible


    IMPORTANT: Each recommendation description MUST be under 80 characters. NO explanations, just the core action.
    """

    expected_output = """
    IMPORTANT: Provide your response ONLY as valid JSON with no additional text or markdown formatting.
    
    Return a comprehensive health improvement plan with MANDATORY evidence URLs in exactly this JSON format:
    {
        "evidence_urls": {
            "alcohol": ["https://url1.com", "https://url2.com"],
            "sleep": ["https://url3.com"],
            "exercise": ["https://url4.com", "https://url5.com"],
            "supplements": ["https://url6.com", "https://url7.com"]
        },
        "recommendations": {
            "alcohol": {
                "description": "Limit to 1 drink per week",
                "rating": <integer 1-10 indicating health benefit of following this recommendation>,
                "evidence_based": true
            },
            "sleep": {
                "description": "Sleep 7-8 hours nightly", 
                "rating": <integer 1-10 indicating future benefit>,
                "evidence_based": true
            },
            "exercise": {
                "description": "150 min cardio + 2x strength training weekly",
                "rating": <integer 1-10 indicating future benefit>,
                "evidence_based": true
            },
            "supplements": [
                {
                    "description": "Omega-3 1000mg daily",
                    "rating": <integer 1-10 indicating future benefit>,
                    "evidence_based": true
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
    
    ALL recommendations MUST have evidence_based: true and be based on the URLs you found.
    The evidence_urls section MUST contain actual URLs from your EXA searches (not placeholder URLs).
    Each category in evidence_urls MUST have at least 1 URL from your searches.
    Recommendations without corresponding URLs are INVALID and will be rejected.
    
    FINAL REMINDER: Each recommendation description MUST be under 80 characters!
    Count the characters! If it's over 80, shorten it further.
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
    Compile all the health recommendations that have been provided by the specialist agents into a final JSON response.
    
    You should have received JSON responses from:
    1. Alcohol Consumption Specialist - JSON with evidence_urls and recommendation
    2. Sleep Quality Specialist - JSON with evidence_urls and recommendation
    3. Exercise Specialist - JSON with evidence_urls and recommendation
    4. Nutritionist - JSON with evidence_urls and recommendations array
    
    IMPORTANT: Each specialist provided their output in JSON format with:
    - evidence_urls: Array of URLs from their EXA searches
    - recommendation/recommendations: Their specific recommendations with descriptions, ratings, and evidence_based flags
    
    BASELINE HEALTH METRICS (current patient status):
    - Current life expectancy: {life_expectancy} years
    - Current cardiovascular risk (10-year): {cardiovascular_risk}
    - Current energy level: {energy_level}
    - Current dementia risk: {dementia_risk}
    - Current metabolic disease risk: {metabolic_risk}
    
    Your task is to:
    1. Parse each specialist's JSON response
    2. Extract the evidence URLs from each specialist
    3. Extract the recommendations from each specialist
    4. Compile everything into the final format below
    5. Add an updated health forecast based on the baseline metrics above
    
    ⚠️ CRITICAL: Preserve the exact recommendation descriptions from specialists!
    They have already been formatted to be under 80 characters. DO NOT modify them.
    
    CRITICAL: The updated health forecast must show substantial, realistic improvements from the BASELINE values:
    - Life expectancy: Increase by 5-10 years from baseline {life_expectancy}
    - Cardiovascular risk: Reduce by 30-50% from baseline {cardiovascular_risk}
    - Energy level: Improve to 'High' if currently {energy_level}
    - Metabolic disease risk: Reduce to 'Low' if currently {metabolic_risk}
    - Dementia risk: Reduce to 'Low' if currently {dementia_risk}
    - Ensure all improvements are evidence-based and achievable

    Ensure all ratings are integers between 1-10. Include all supplement recommendations from the nutritionist.
    The forecast should show optimistic, positive improvements based on following all recommendations.
    
    IMPORTANT: Your output must be ONLY the JSON response with no additional text or explanation.
    """

    expected_output = """
    Return ONLY this JSON structure with no additional text:
    {
        "evidence_urls": {
            "alcohol": [<URLs from alcohol specialist>],
            "sleep": [<URLs from sleep specialist>],
            "exercise": [<URLs from exercise specialist>],
            "supplements": [<URLs from nutritionist>]
        },
        "recommendations": {
            "alcohol": {
                "description": <exact description from alcohol specialist>,
                "rating": <rating from alcohol specialist>,
                "evidence_based": true
            },
            "sleep": {
                "description": <exact description from sleep specialist>, 
                "rating": <rating from sleep specialist>,
                "evidence_based": true
            },
            "exercise": {
                "description": <exact description from exercise specialist>,
                "rating": <rating from exercise specialist>,
                "evidence_based": true
            },
            "supplements": [
                {
                    "description": <exact description from nutritionist>,
                    "rating": <rating from nutritionist>,
                    "evidence_based": true
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


def create_single_agent_crew() -> Crew:
    """
    Create a crew with a single comprehensive PCP agent.

    Returns:
        Crew: The configured single-agent crew
    """
    # Create the single comprehensive PCP agent
    single_pcp = create_single_pcp_agent()

    # Create the comprehensive task
    comprehensive_task = create_single_pcp_task(single_pcp)

    # Return crew with single agent and task
    return Crew(
        agents=[single_pcp],
        tasks=[comprehensive_task],
        process=Process.sequential,  # Sequential process (though only one task)
        verbose=True,
        max_rpm=None,
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
    # mode: str = "single_agent",
    mode: str = "multi_agent",
) -> Dict[str, Any]:
    """
    Run the patient health assessment crew asynchronously.

    Args:
        patient_data: Patient data dictionary
        mode: Execution mode - "multi_agent" (default) or "single_agent"

    Returns:
        Dict containing health recommendations
    """
    # Get logger
    logger = get_logger(__name__)

    # Flatten patient data into inputs
    inputs = flatten_patient_data(patient_data)

    logger.info("Using multi-agent mode")
    crew = create_crew()
    result = await crew.kickoff_async(inputs)

    crew = create_single_agent_crew()

    try:
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
