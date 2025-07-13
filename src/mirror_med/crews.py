"""
Patient Health Assessment Crew
==============================

This module implements a hierarchical CrewAI crew that acts as a digital twin
for patient health assessments. The crew simulates a visit to a primary care
physician (PCP) who coordinates with various specialists to create a
comprehensive health improvement plan.

The crew uses a hierarchical process where the PCP acts as the manager,
delegating specific assessments to nutrition, sleep, and exercise specialists.
"""

import json
from typing import Any, Dict

from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import EXASearchTool

from mirror_med.logging import get_logger


class PatientHealthCrew:
    """
    A hierarchical crew that simulates a patient's visit to a PCP
    for a comprehensive health assessment and improvement plan.
    """

    def __init__(self):
        """Initialize the crew with tools and agents."""
        # Initialize logger
        self.logger = get_logger(__name__)

        # Initialize tools
        self.search_tool = EXASearchTool()

        # Initialize agents
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all medical specialist agents."""
        # Configure LLM for all agents
        agent_llm = LLM(model="openai/gpt-4.1-nano")

        # Primary Care Physician (Manager)
        self.pcp = Agent(
            role="Primary Care Physician",
            goal="Coordinate comprehensive health assessment and create personalized health improvement plan based on patient data and specialist recommendations",
            backstory="""You are a board-certified Internal Medicine physician with 20 years 
            of experience in primary care and preventive medicine. You excel at synthesizing 
            information from various specialists to create holistic health plans. You follow 
            evidence-based guidelines from the ACP, AAFP, and USPSTF. You have a special 
            interest in lifestyle medicine and preventive care. You are responsible for 
            making alcohol consumption recommendations based on the patient's current habits 
            and health status.""",
            tools=[self.search_tool],
            verbose=True,
            allow_delegation=True,  # Critical for hierarchical process
            max_iter=3,
            llm=agent_llm,
        )

        # Nutrition Specialist
        self.nutrition_specialist = Agent(
            role="Clinical Nutrition Specialist",
            goal="Analyze dietary patterns and recommend evidence-based nutritional supplements to optimize health",
            backstory="""You are a Registered Dietitian Nutritionist (RDN) with a PhD in 
            Nutritional Sciences and 15 years of clinical experience. You specialize in 
            preventive nutrition, micronutrient optimization, and evidence-based supplement 
            recommendations. You stay current with the latest research on nutritional 
            supplements and their interactions. You consider the patient's diet, medical 
            conditions, medications, and lab values when making supplement recommendations.""",
            tools=[self.search_tool],
            verbose=True,
            allow_delegation=False,
            llm=agent_llm,
        )

        # Sleep Medicine Specialist
        self.sleep_specialist = Agent(
            role="Sleep Medicine Physician",
            goal="Optimize sleep quality and duration for improved health outcomes and disease prevention",
            backstory="""You are a board-certified Sleep Medicine physician with expertise 
            in sleep hygiene, circadian rhythm optimization, and the relationship between 
            sleep and chronic disease. You have 18 years of experience helping patients 
            improve their sleep without medication when possible. You understand the impact 
            of sleep on metabolism, cardiovascular health, cognitive function, and overall 
            well-being. You provide practical, evidence-based recommendations for sleep 
            improvement.""",
            tools=[self.search_tool],
            verbose=True,
            allow_delegation=False,
            llm=agent_llm,
        )

        # Exercise Physiologist
        self.exercise_specialist = Agent(
            role="Exercise Physiologist",
            goal="Design optimal fitness routines for cardiovascular health, longevity, and disease prevention",
            backstory="""You are a certified Clinical Exercise Physiologist (CEP) with a 
            Master's degree in Exercise Science and 12 years of experience. You specialize 
            in endurance training, cardiovascular fitness, and exercise prescription for 
            health optimization. You understand the dose-response relationship of exercise 
            and can tailor recommendations based on current fitness levels, injury history, 
            and health goals. You stay current with research on exercise for longevity and 
            chronic disease prevention.""",
            tools=[self.search_tool],
            verbose=True,
            allow_delegation=False,
            llm=agent_llm,
        )

    def create_health_assessment_task(self, patient_data: Dict[str, Any]) -> Task:
        """
        Create the comprehensive health assessment task with patient data.

        Args:
            patient_data: Dictionary containing patient health information

        Returns:
            Task: The configured health assessment task
        """
        task_description = f"""
        Conduct a brief health assessment for a patient visit with the following data:
        
        PATIENT INFORMATION:
        - Social History:
          * Diet: {patient_data["social_history"]["food"]}
          * Exercise: {patient_data["social_history"]["exercise"]["description"]} (current rating: {patient_data["social_history"]["exercise"]["rating"]}/10)
          * Alcohol: {patient_data["social_history"]["alcohol"]["description"]} (current rating: {patient_data["social_history"]["alcohol"]["rating"]}/10)
          * Sleep: {patient_data["social_history"]["sleep"]["description"]} (current rating: {patient_data["social_history"]["sleep"]["rating"]}/10)
          * Occupation: {patient_data["social_history"]["occupation"]}
        
        - Medical History: {", ".join(patient_data["medical_history"]["conditions"])}
        - Current Medications: {", ".join([f"{med['name']} {med['dose']}" for med in patient_data["medications"]])}
        - Allergies: {", ".join([f"{allergy['allergen']} ({allergy['reaction']})" for allergy in patient_data["allergies"]])}
        - Family History: Father - {", ".join(patient_data["family_history"]["father"])}, Mother - {", ".join(patient_data["family_history"]["mother"])}
        
        - Vital Signs & Measurements:
          * Weight: {patient_data["measurements"]["weight"]} lbs
          * Height: {patient_data["measurements"]["height"]} inches
          * Blood Pressure: {patient_data["measurements"]["blood_pressure"]}
          * Cholesterol: Total {patient_data["measurements"]["cholesterol"]}, HDL {patient_data["measurements"]["hdl"]}, LDL {patient_data["measurements"]["ldl"]}
          * Triglycerides: {patient_data["measurements"]["triglycerides"]}
        
        - Health Forecast:
          * Cardiovascular risk (10-year): {patient_data["forecast"]["cardiovascular_event_10yr_probability"]}
          * Dementia risk: {patient_data["forecast"]["dementia_risk"]}
          * Metabolic disease risk: {patient_data["forecast"]["metabolic_disease_risk"]}
        
        As the Primary Care Physician, coordinate with your specialist team to develop a health improvement plan.
        
        You should:
        
        1. Assess alcohol consumption and provide specific recommendations for optimization
        2. Delegate sleep assessment to the Sleep Medicine Specialist
        3. Delegate exercise evaluation to the Exercise Physiologist  
        4. Delegate nutritional supplement assessment to the Nutrition Specialist
        
        Synthesize all specialist recommendations into a cohesive plan that addresses the patient's risk factors.
        """

        expected_output = """
        A comprehensive health improvement plan in the following JSON format:
        {
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
                },
                ...
            ]
        }
        """

        return Task(
            description=task_description,
            expected_output=expected_output,
            agent=self.pcp,
        )

    def create_crew(self, patient_data: Dict[str, Any]) -> Crew:
        """
        Create the hierarchical crew for patient health assessment.

        Args:
            patient_data: Dictionary containing patient health information

        Returns:
            Crew: The configured hierarchical crew
        """
        # Create the task
        health_assessment_task = self.create_health_assessment_task(patient_data)

        # Create and return the crew
        return Crew(
            agents=[
                self.pcp,
                self.nutrition_specialist,
                self.sleep_specialist,
                self.exercise_specialist,
            ],
            tasks=[health_assessment_task],
            process=Process.hierarchical,
            manager_llm="openai/gpt-4.1-nano",  # Use GPT-4.1-nano for manager decisions
            verbose=True,
            memory=True,  # Enable memory for better context
            max_rpm=30,  # Rate limiting
            step_callback=lambda step: self.logger.info("Step completed", step=step),
        )


def run_patient_health_assessment(
    patient_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run the patient health assessment crew.

    Args:
        patient_data: Optional patient data dictionary. If not provided,
                     loads from smash.json

    Returns:
        Dict containing health recommendations
    """
    # Get logger
    logger = get_logger(__name__)

    # Create the crew
    health_crew = PatientHealthCrew()
    crew = health_crew.create_crew(patient_data)

    try:
        logger.info("Starting patient health assessment")
        result = crew.kickoff()

        # Try to parse the result as JSON
        try:
            # Extract JSON from the result if it's embedded in text
            import re

            json_match = re.search(r"\{[\s\S]*\}", str(result))
            if json_match:
                recommendations = json.loads(json_match.group())
                logger.info(
                    "Successfully parsed recommendations",
                    recommendations_count=len(recommendations),
                )
                return recommendations
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
