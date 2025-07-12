from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message


class HelloWorldAgentExecutor(AgentExecutor):
    """A simple hello world agent executor for MirrorMed."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute the hello world agent task."""
        await event_queue.enqueue_event(
            new_agent_text_message("Hello from MirrorMed A2A Agent!")
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel is not supported for this simple agent."""
        raise Exception("Cancel not supported")