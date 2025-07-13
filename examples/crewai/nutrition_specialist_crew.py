"""
Nutrition Specialist AI Agent Crew
==================================

This example demonstrates how to create a comprehensive nutrition specialist team
using CrewAI. The crew includes a clinical nutritionist, meal planner, and
supplement advisor working together to provide personalized nutrition care.

Requirements:
- crewai
- crewai_tools
- exa_py
"""

from crewai_tools import FileReadTool, EXASearchTool

from crewai import Agent, Crew, Process, Task

# Initialize tools
# EXASearchTool requires EXA_API_KEY environment variable to be set
search_tool = EXASearchTool()
file_tool = FileReadTool()

# Define Nutrition Specialist Agents
nutritionist = Agent(
    role="Clinical Nutritionist",
    goal="Provide evidence-based nutritional assessments and personalized meal plans",
    backstory="""You are a registered dietitian with 15 years of experience in clinical 
    nutrition. You specialize in creating personalized nutrition plans based on medical 
    conditions, dietary restrictions, and health goals. You stay current with the latest 
    nutrition research and guidelines from professional organizations.""",
    tools=[search_tool],
    verbose=True,
    allow_delegation=True,
)

meal_planner = Agent(
    role="Meal Planning Specialist",
    goal="Create practical, delicious meal plans that meet nutritional requirements",
    backstory="""You are a culinary nutrition expert who transforms nutritional 
    guidelines into practical, enjoyable meal plans. You consider cultural preferences, 
    cooking skills, budget constraints, and time availability when designing meals.""",
    tools=[file_tool],
    verbose=True,
)

supplement_advisor = Agent(
    role="Supplement and Micronutrient Expert",
    goal="Analyze micronutrient needs and recommend appropriate supplementation",
    backstory="""You are a clinical pharmacist specializing in nutritional supplements. 
    You understand drug-nutrient interactions, bioavailability, and evidence-based 
    supplementation protocols. You prioritize food-first approaches while recognizing 
    when supplements are beneficial.""",
    tools=[search_tool],
    verbose=True,
)

# Define Tasks
assessment_task = Task(
    description="""Conduct a comprehensive nutritional assessment for a patient with:
    - Age: {age}
    - Medical conditions: {conditions}
    - Current medications: {medications}
    - Dietary restrictions: {restrictions}
    - Health goals: {goals}
    
    Analyze their nutritional needs, identify potential deficiencies, and determine 
    caloric and macronutrient requirements.""",
    expected_output="""A detailed nutritional assessment report including:
    - Estimated caloric needs
    - Macronutrient distribution (proteins, carbs, fats)
    - Key micronutrient considerations
    - Potential nutrient-drug interactions
    - Priority nutritional interventions""",
    agent=nutritionist,
)

meal_plan_task = Task(
    description="""Based on the nutritional assessment, create a 7-day meal plan that:
    - Meets all identified nutritional requirements
    - Respects dietary restrictions and preferences
    - Includes practical recipes with preparation times
    - Provides shopping lists and meal prep tips
    - Offers alternatives for different scenarios (eating out, busy days)""",
    expected_output="""A complete 7-day meal plan with:
    - Daily menus for breakfast, lunch, dinner, and snacks
    - Detailed recipes with nutritional information
    - Weekly shopping list organized by food groups
    - Meal preparation schedule and tips
    - Restaurant ordering guidelines""",
    agent=meal_planner,
    context=[assessment_task],
)

supplement_task = Task(
    description="""Review the nutritional assessment and meal plan to:
    - Identify any remaining nutritional gaps
    - Recommend evidence-based supplements if needed
    - Consider medication interactions
    - Provide dosing and timing recommendations
    - Suggest monitoring parameters""",
    expected_output="""A supplement recommendation report including:
    - Specific supplements with dosages and forms
    - Timing recommendations for optimal absorption
    - Potential interactions to monitor
    - Duration of supplementation
    - Follow-up testing recommendations""",
    agent=supplement_advisor,
    context=[assessment_task, meal_plan_task],
)

# Create the Nutrition Crew
nutrition_crew = Crew(
    agents=[nutritionist, meal_planner, supplement_advisor],
    tasks=[assessment_task, meal_plan_task, supplement_task],
    process=Process.sequential,
    verbose=True,
)


def run_nutrition_assessment(patient_data: dict):
    """
    Run a comprehensive nutrition assessment for a patient.

    Args:
        patient_data: Dictionary containing patient information including:
            - age: Patient's age
            - conditions: Medical conditions
            - medications: Current medications
            - restrictions: Dietary restrictions
            - goals: Health goals

    Returns:
        CrewOutput: Results from the nutrition crew analysis
    """
    return nutrition_crew.kickoff(inputs=patient_data)


if __name__ == "__main__":
    # Example usage
    patient_data = {
        "age": "45",
        "conditions": "Type 2 diabetes, hypertension",
        "medications": "Metformin 1000mg bid, Lisinopril 10mg daily",
        "restrictions": "Lactose intolerant, prefers Mediterranean-style diet",
        "goals": "Weight loss (20 lbs), improve blood sugar control",
    }

    print("Starting Nutrition Specialist Crew Assessment...")
    print("=" * 50)

    result = run_nutrition_assessment(patient_data)

    print("\n" + "=" * 50)
    print("FINAL NUTRITION CARE PLAN:")
    print("=" * 50)
    print(result)
