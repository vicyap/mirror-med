# CrewAI Healthcare Examples

This directory contains examples of using CrewAI to build collaborative AI agent teams for healthcare applications.

## Overview

CrewAI is a framework for orchestrating multiple AI agents that work together to solve complex problems. These examples demonstrate how to create specialized healthcare teams that mimic real-world clinical workflows.

## Examples

### 1. Nutrition Specialist Crew (`nutrition_specialist_crew.py`)

A comprehensive nutrition care team that includes:
- **Clinical Nutritionist**: Performs nutritional assessments and creates personalized plans
- **Meal Planning Specialist**: Develops practical meal plans with recipes and shopping lists
- **Supplement Advisor**: Analyzes micronutrient needs and recommends evidence-based supplementation

**Use Cases:**
- Diabetes nutrition management
- Weight loss programs
- Medical nutrition therapy
- Dietary restriction planning

### 2. Primary Care Physician (PCP) Crew (`pcp_specialist_crew.py`)

A complete primary care team featuring:
- **Primary Care Physician**: Conducts assessments and develops treatment plans
- **Preventive Care Specialist**: Manages screenings and preventive services
- **Care Coordinator**: Handles referrals and care transitions
- **Health Educator**: Creates patient education materials

**Use Cases:**
- Annual wellness visits
- Chronic disease management
- Preventive care planning
- Care coordination

### 3. Advanced PCP Crew with Clinical Decision Support (`advanced_pcp_crew.py`)

An enhanced version with additional capabilities:
- All agents from the basic PCP crew
- **Clinical Decision Support Specialist**: Provides drug interaction checks, guideline adherence, and safety alerts
- Hierarchical process management for complex cases
- Quality metric tracking
- Enhanced safety features

**Use Cases:**
- Complex multi-morbidity patients
- Polypharmacy management
- Quality improvement initiatives
- Clinical pathway implementation

## Installation

```bash
# Install CrewAI (already added to pyproject.toml)
uv sync

# Install additional tools if needed
uv add crewai-tools
```

## Configuration

Before running the examples, ensure you have the necessary API keys:

```bash
# Set OpenAI API key (required for agent LLMs)
export OPENAI_API_KEY="your-openai-api-key"

# Set Serper API key (required for web search tool)
export SERPER_API_KEY="your-serper-api-key"
```

## Running the Examples

### Basic Usage

```python
from examples.crewai.nutrition_specialist_crew import run_nutrition_assessment

# Patient data for nutrition assessment
patient_data = {
    "age": "45",
    "conditions": "Type 2 diabetes, hypertension",
    "medications": "Metformin 1000mg bid, Lisinopril 10mg daily",
    "restrictions": "Lactose intolerant",
    "goals": "Weight loss, improve blood sugar"
}

result = run_nutrition_assessment(patient_data)
print(result)
```

### Running Standalone

Each example can be run independently:

```bash
# Run nutrition specialist crew
uv run python examples/crewai/nutrition_specialist_crew.py

# Run PCP specialist crew
uv run python examples/crewai/pcp_specialist_crew.py

# Run advanced PCP crew
uv run python examples/crewai/advanced_pcp_crew.py
```

## Key Concepts

### Agents
- Each agent has a specific role, goal, and backstory
- Agents can use tools (search, file reading, etc.)
- Agents can delegate tasks to other agents

### Tasks
- Define specific objectives with expected outputs
- Can have context from previous tasks
- Support variable interpolation from input data

### Crews
- Orchestrate multiple agents and tasks
- Support different processes (sequential, hierarchical)
- Can maintain memory across interactions

### Processes
- **Sequential**: Tasks execute one after another
- **Hierarchical**: Manager agent coordinates team members

## Customization

These examples can be customized by:

1. **Adding New Agents**: Create agents with specialized roles
2. **Modifying Tasks**: Adjust descriptions and expected outputs
3. **Changing Tools**: Add domain-specific tools for agents
4. **Adjusting Process**: Switch between sequential and hierarchical
5. **Adding Memory**: Enable persistent memory for continuity

## Best Practices

1. **Clear Role Definition**: Give agents specific, well-defined roles
2. **Detailed Backstories**: Rich backstories improve agent behavior
3. **Structured Outputs**: Define clear expected outputs for tasks
4. **Tool Selection**: Choose appropriate tools for each agent
5. **Error Handling**: Include validation and error handling
6. **Rate Limiting**: Set appropriate rate limits for API calls

## Integration with A2A

These CrewAI examples can be integrated with the A2A (Agent-to-Agent) protocol:

```python
# See a2a-samples/samples/python/agents/crewai/ for A2A integration examples
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set
2. **Rate Limiting**: Adjust `max_rpm` parameter if hitting limits
3. **Memory Issues**: For large contexts, adjust `max_iter` and enable `respect_context_window`
4. **Tool Failures**: Verify tool dependencies and permissions

### Debug Mode

Enable verbose output for debugging:

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    verbose=True,  # Enable detailed logging
    step_callback=lambda step: print(f"Step: {step}")  # Track progress
)
```

## Resources

- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI GitHub](https://github.com/crewAIInc/crewAI)
- [CrewAI Blog](https://blog.crewai.com)
- [Community Forum](https://community.crewai.com)

## License

These examples are provided as-is for educational and development purposes.