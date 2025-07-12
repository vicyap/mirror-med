from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from mirror_med.a2a.hello_executor import HelloWorldAgentExecutor


def create_a2a_app(base_url: str):
    """Create an A2A application with the given base URL."""
    skill = AgentSkill(
        id="hello_world",
        name="Hello World",
        description="Returns a greeting from MirrorMed",
        tags=["greeting", "test"],
        examples=["hello", "hi"],
    )

    agent_card = AgentCard(
        name="MirrorMed Agent",
        description="A medical information A2A agent (hello world test)",
        url=base_url,
        version="0.1.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    return server.build()
