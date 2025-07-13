"""
Advanced PCP Crew with Clinical Decision Support
================================================

This example demonstrates an enhanced primary care team that includes clinical
decision support capabilities. The crew uses hierarchical process management
for complex decision-making and includes safety checks, drug interactions,
and guideline adherence verification.

Requirements:
- crewai
- crewai_tools
- exa_py
"""

from typing import Any, Dict

from crewai_tools import FileReadTool, EXASearchTool

from crewai import Agent, Crew, Process, Task

# Initialize tools
# EXASearchTool requires EXA_API_KEY environment variable to be set
search_tool = EXASearchTool()
file_tool = FileReadTool()

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

clinical_decision_agent = Agent(
    role="Clinical Decision Support Specialist",
    goal="Provide evidence-based clinical decision support and guideline recommendations",
    backstory="""You are an AI-powered clinical decision support system trained on 
    the latest medical guidelines, clinical pathways, and quality measures. You help 
    ensure adherence to best practices and identify potential drug interactions, 
    contraindications, and clinical alerts.""",
    tools=[search_tool],
    verbose=True,
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
    - Vital signs: {vitals}
    - Lab results (if available): {labs}
    
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

decision_support_task = Task(
    description="""Analyze the assessment and treatment plan to:
    - Check for drug-drug interactions
    - Verify dosing appropriateness based on renal/hepatic function
    - Confirm guideline adherence (JNC8, ADA, ACC/AHA)
    - Identify quality metric gaps (HEDIS, MIPS)
    - Suggest clinical pathways
    - Flag safety concerns and contraindications
    - Review for potential adverse drug events""",
    expected_output="""Clinical decision support report with:
    - Drug interaction alerts with severity levels
    - Dosing recommendations with adjustments if needed
    - Guideline compliance assessment with specific recommendations
    - Quality metric performance and gaps
    - Clinical pathway recommendations
    - Safety alerts and contraindications
    - Alternative treatment options if issues identified""",
    agent=clinical_decision_agent,
    context=[initial_assessment_task],
)

preventive_screening_task = Task(
    description="""Based on patient demographics, risk factors, and clinical guidelines:
    - Review current preventive care status
    - Identify overdue screenings per USPSTF guidelines
    - Recommend age-appropriate preventive services
    - Consider risk-based screening beyond standard guidelines
    - Address immunization needs per CDC schedule
    - Calculate cardiovascular risk scores (ASCVD, Framingham)""",
    expected_output="""Comprehensive preventive care plan including:
    - Overdue screenings with priority levels and timeframes
    - Recommended vaccines with schedules and contraindications
    - Lifestyle counseling priorities with specific interventions
    - Cancer screening recommendations with rationale
    - Cardiovascular risk assessment with interventions
    - Bone health assessment if indicated
    - Timeline and tracking system for each service""",
    agent=preventive_care_specialist,
    context=[initial_assessment_task, decision_support_task],
)

care_coordination_task = Task(
    description="""Develop a comprehensive care coordination plan that:
    - Organizes specialist referrals with specific clinical questions
    - Schedules follow-up appointments with appropriate intervals
    - Coordinates diagnostic testing with proper sequencing
    - Identifies and addresses care barriers
    - Creates tracking system for all recommendations
    - Ensures care transitions are smooth
    - Coordinates with pharmacy for medication management""",
    expected_output="""Detailed care coordination plan including:
    - Referral matrix with urgency levels and clinical questions
    - Pre-authorization requirements and insurance considerations
    - Testing schedule with prep instructions and timing
    - Follow-up appointment calendar with reminders
    - Barrier mitigation strategies
    - Communication plan for results and handoffs
    - Medication reconciliation and pharmacy coordination
    - Patient portal activation and usage guide""",
    agent=care_coordinator,
    context=[initial_assessment_task, decision_support_task, preventive_screening_task],
)

education_plan_task = Task(
    description="""Create a comprehensive patient education plan that:
    - Explains diagnoses in patient-friendly language
    - Provides medication education with visual aids
    - Develops SMART goals for lifestyle modifications
    - Identifies warning signs and when to seek care
    - Includes self-monitoring tools and logs
    - Addresses health literacy and cultural considerations
    - Provides reliable resources and support groups""",
    expected_output="""Complete patient education package including:
    - Condition fact sheets with illustrations
    - Medication guide with dosing calendar and side effects
    - Personalized SMART goals worksheet
    - Red flag symptoms action plan
    - Self-monitoring logs (BP, glucose, weight, etc.)
    - Community resources directory
    - Follow-up questions checklist
    - Emergency contact information card""",
    agent=health_educator,
    context=[initial_assessment_task, decision_support_task, preventive_screening_task],
)

# Create enhanced crew with hierarchical process for complex decision-making
enhanced_pcp_crew = Crew(
    agents=[
        primary_physician,
        clinical_decision_agent,
        preventive_care_specialist,
        care_coordinator,
        health_educator,
    ],
    tasks=[
        initial_assessment_task,
        decision_support_task,
        preventive_screening_task,
        care_coordination_task,
        education_plan_task,
    ],
    process=Process.hierarchical,  # Use hierarchical for complex decision-making
    manager_llm="gpt-4o",  # Specify the manager model
    verbose=True,
    memory=True,  # Enable memory for continuity
    max_rpm=30,  # Rate limiting for API calls
    step_callback=lambda step: print(
        f"\n[STEP COMPLETED]: {step}\n"
    ),  # Progress tracking
)


def run_advanced_pcp_assessment(patient_data: Dict[str, Any]) -> Any:
    """
    Run an advanced primary care assessment with clinical decision support.

    Args:
        patient_data: Dictionary containing comprehensive patient information

    Returns:
        CrewOutput: Results from the enhanced PCP crew analysis
    """
    # Validate required fields
    required_fields = ["chief_complaint", "age", "sex", "medications"]
    missing_fields = [field for field in required_fields if field not in patient_data]

    if missing_fields:
        raise ValueError(f"Missing required patient data fields: {missing_fields}")

    # Set defaults for optional fields
    defaults = {
        "pmh": "None documented",
        "allergies": "NKDA",
        "social_history": "Not provided",
        "family_history": "Non-contributory",
        "ros": "Not performed",
        "vitals": "Not available",
        "labs": "No recent labs",
    }

    # Apply defaults for missing optional fields
    for field, default in defaults.items():
        if field not in patient_data:
            patient_data[field] = default

    return enhanced_pcp_crew.kickoff(inputs=patient_data)


if __name__ == "__main__":
    # Example usage with comprehensive patient data
    patient_data = {
        "chief_complaint": "Uncontrolled diabetes and new onset chest pressure",
        "age": "62",
        "sex": "Male",
        "pmh": "Type 2 DM (15 years), HTN (10 years), Hyperlipidemia (8 years), OSA on CPAP",
        "medications": """Metformin 1000mg BID, Glipizide 10mg daily, Lisinopril 20mg daily,
                         Atorvastatin 40mg daily, Aspirin 81mg daily""",
        "allergies": "Sulfa (hives), Contrast dye (anaphylaxis)",
        "social_history": "Current smoker (30 pack-years), Alcohol 2-3 beers/day, Sedentary",
        "family_history": "Father: MI at 55, Mother: T2DM, Brother: Stroke at 60",
        "ros": """Positive: Polyuria, polydipsia, blurred vision, chest pressure with exertion,
                 fatigue, numbness in feet. Negative: Syncope, palpitations, orthopnea""",
        "vitals": "BP 156/94, HR 88, RR 18, Temp 98.6, O2 98% RA, BMI 34",
        "labs": """HbA1c 9.2%, FBG 186, Cr 1.3, eGFR 58, LDL 142, HDL 38, Trig 220,
                  ALT 45, AST 38, K 4.2, Na 138""",
    }

    print("Starting Advanced Primary Care Assessment with Clinical Decision Support...")
    print("=" * 70)

    try:
        result = run_advanced_pcp_assessment(patient_data)

        print("\n" + "=" * 70)
        print("COMPREHENSIVE CARE PLAN WITH CLINICAL DECISION SUPPORT:")
        print("=" * 70)
        print(result)

    except Exception as e:
        print(f"Error during assessment: {e}")
        raise
