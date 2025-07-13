"""
Primary Care Physician (PCP) Specialist AI Agent Crew
=====================================================

This example demonstrates how to create a comprehensive primary care team using CrewAI.
The crew includes a primary physician, care coordinator, preventive care specialist,
and health educator working together to provide complete patient care.

Requirements:
- crewai
- crewai_tools
- exa_py
"""


from crewai_tools import FileReadTool, EXASearchTool

from crewai import Agent, Crew, Process, Task

# Initialize tools
# EXASearchTool requires EXA_API_KEY environment variable to be set
search_tool = EXASearchTool()  # For medical literature searches
file_tool = FileReadTool()  # For accessing patient records

# Define PCP Specialist Agents
primary_physician = Agent(
    role="Primary Care Physician",
    goal="Provide comprehensive primary care assessment and treatment planning",
    backstory="""You are a board-certified Internal Medicine physician with 20 years 
    of experience in primary care. You excel at diagnosing common conditions, managing 
    chronic diseases, and coordinating care. You follow evidence-based guidelines from 
    the ACP, AAFP, and USPSTF. You prioritize preventive care and patient education.""",
    tools=[search_tool],
    verbose=True,
    allow_delegation=True,
    max_iter=30,
)

care_coordinator = Agent(
    role="Clinical Care Coordinator",
    goal="Ensure seamless care coordination and follow-up management",
    backstory="""You are a registered nurse with expertise in care coordination and 
    case management. You track referrals, ensure patients complete recommended tests, 
    coordinate with specialists, and manage care transitions. You're skilled at 
    identifying barriers to care and finding solutions.""",
    tools=[file_tool],
    verbose=True,
)

preventive_care_specialist = Agent(
    role="Preventive Medicine Specialist",
    goal="Optimize preventive care and health screening recommendations",
    backstory="""You are a preventive medicine specialist who ensures patients receive 
    appropriate screenings and preventive interventions based on their age, risk factors, 
    and guidelines. You stay current with USPSTF recommendations and quality metrics.""",
    tools=[search_tool],
    verbose=True,
)

health_educator = Agent(
    role="Patient Health Educator",
    goal="Provide clear, actionable patient education and self-management support",
    backstory="""You are a certified diabetes educator and health coach with expertise 
    in patient education. You translate complex medical information into understandable 
    language and create personalized education plans that promote behavior change.""",
    verbose=True,
)

# Define Tasks
initial_assessment_task = Task(
    description="""Conduct a comprehensive primary care assessment for a patient with:
    - Chief complaint: {chief_complaint}
    - Age: {age}, Sex: {sex}
    - Past medical history: {pmh}
    - Current medications: {medications}
    - Allergies: {allergies}
    - Social history: {social_history}
    - Family history: {family_history}
    - Review of systems: {ros}
    
    Perform differential diagnosis, identify red flags, and develop initial management plan.""",
    expected_output="""A comprehensive assessment including:
    - Problem list with ICD-10 codes
    - Differential diagnosis with reasoning
    - Recommended diagnostic tests with rationale
    - Initial treatment plan
    - Follow-up timeline
    - Specialty referral needs""",
    agent=primary_physician,
)

preventive_screening_task = Task(
    description="""Based on patient demographics and risk factors:
    - Review current preventive care status
    - Identify overdue screenings
    - Recommend age-appropriate preventive services
    - Consider risk-based screening beyond standard guidelines
    - Address immunization needs""",
    expected_output="""Preventive care plan including:
    - Overdue screenings with priority levels
    - Recommended vaccines with schedules
    - Lifestyle counseling priorities
    - Cancer screening recommendations
    - Cardiovascular risk assessment and interventions
    - Timeline for each preventive service""",
    agent=preventive_care_specialist,
    context=[initial_assessment_task],
)

care_coordination_task = Task(
    description="""Develop a comprehensive care coordination plan:
    - Organize specialist referrals with specific questions
    - Schedule follow-up appointments
    - Coordinate diagnostic testing
    - Identify care barriers and solutions
    - Create tracking system for all recommendations""",
    expected_output="""Care coordination checklist including:
    - Referral details with urgency levels
    - Pre-authorization requirements
    - Testing schedule with prep instructions
    - Follow-up appointment timeline
    - Patient navigator resources
    - Communication plan for results""",
    agent=care_coordinator,
    context=[initial_assessment_task, preventive_screening_task],
)

education_plan_task = Task(
    description="""Create a personalized patient education plan addressing:
    - Key diagnoses and what they mean
    - Medication education with adherence strategies
    - Lifestyle modifications with specific goals
    - Warning signs requiring immediate care
    - Self-management tools and resources""",
    expected_output="""Patient education package including:
    - Simplified explanation of conditions
    - Medication guide with visual aids
    - SMART goals for lifestyle changes
    - Red flag symptoms checklist
    - Community resources and support groups
    - Follow-up questions to ask providers""",
    agent=health_educator,
    context=[initial_assessment_task, preventive_screening_task],
)

# Create the PCP Crew with sequential process
pcp_crew = Crew(
    agents=[
        primary_physician,
        preventive_care_specialist,
        care_coordinator,
        health_educator,
    ],
    tasks=[
        initial_assessment_task,
        preventive_screening_task,
        care_coordination_task,
        education_plan_task,
    ],
    process=Process.sequential,
    verbose=True,
    memory=True,  # Enable memory for continuity of care
)


def run_pcp_assessment(patient_data: dict):
    """
    Run a comprehensive primary care assessment for a patient.

    Args:
        patient_data: Dictionary containing patient information including:
            - chief_complaint: Main reason for visit
            - age: Patient's age
            - sex: Patient's sex
            - pmh: Past medical history
            - medications: Current medications
            - allergies: Known allergies
            - social_history: Social history
            - family_history: Family medical history
            - ros: Review of systems

    Returns:
        CrewOutput: Results from the PCP crew analysis
    """
    return pcp_crew.kickoff(inputs=patient_data)


if __name__ == "__main__":
    # Example usage for a complex patient
    patient_data = {
        "chief_complaint": "Fatigue and shortness of breath for 3 months",
        "age": "58",
        "sex": "Female",
        "pmh": "Type 2 diabetes (10 years), Hypertension (5 years), Obesity (BMI 32)",
        "medications": "Metformin 1000mg BID, Amlodipine 5mg daily, Atorvastatin 20mg daily",
        "allergies": "Penicillin (rash)",
        "social_history": "Former smoker (quit 2 years ago, 20 pack-years), social drinker",
        "family_history": "Mother: breast cancer at 65, Father: MI at 62",
        "ros": "Positive for fatigue, DOE, occasional palpitations. Negative for chest pain, orthopnea",
    }

    print("Starting Primary Care Assessment...")
    print("=" * 50)

    # Run the crew
    result = run_pcp_assessment(patient_data)

    print("\n" + "=" * 50)
    print("COMPREHENSIVE CARE PLAN:")
    print("=" * 50)
    print(result)
