from functools import lru_cache

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from ..settings import get_settings
from .hello_executor import HelloWorldAgentExecutor


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


def get_agent_url_from_request(request):
    """Extract the base URL from the request dynamically."""
    # Build URL from request components
    scheme = request.url.scheme
    host = request.headers.get("host", request.url.netloc)

    # Handle X-Forwarded headers for proxy scenarios
    forwarded_proto = request.headers.get("x-forwarded-proto")
    forwarded_host = request.headers.get("x-forwarded-host")

    if forwarded_proto:
        scheme = forwarded_proto
    if forwarded_host:
        host = forwarded_host

    return f"{scheme}://{host}"


@lru_cache(maxsize=128)
def _create_cached_app(base_url: str):
    """Internal function to create and cache A2A apps by base URL."""
    return create_a2a_app(base_url)


def get_or_create_a2a_app(request):
    """Get or create an A2A app based on the request URL or settings."""
    settings = get_settings()
    
    if settings.a2a_base_url:
        # Use configured base URL if provided
        base_url = settings.a2a_base_url
    else:
        # Dynamically determine base URL from request
        base_url = get_agent_url_from_request(request) + "/a2a"
    
    return _create_cached_app(base_url)
