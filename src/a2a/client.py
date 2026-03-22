"""A2A HTTP client — used by the Main Agent to call the Search Agent."""

import structlog
import httpx
from app.core.config import settings
from src.a2a.protocol import Task, TaskSendParams, Message, AgentCard

logger = structlog.get_logger()


class A2AClient:
    """Async HTTP client that speaks the A2A protocol.

    The Main Agent uses this to send tasks to the Content Search Agent
    and retrieve results.
    """

    def __init__(self, agent_url: str | None = None) -> None:
        self.base_url = (agent_url or settings.search_agent_url).rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.search_agent_port and 30.0,
        )
        logger.info("a2a_client_initialized", agent_url=self.base_url)

    async def get_agent_card(self) -> AgentCard:
        """Fetch the search agent's capability card.

        Returns:
            AgentCard describing the search agent's skills.
        """
        response = await self._http.get("/.well-known/agent.json")
        response.raise_for_status()
        return AgentCard(**response.json())

    async def send_task(self, query: str, metadata: dict | None = None) -> Task:
        """Submit a search task to the Content Search Agent.

        Args:
            query: The natural language search query.
            metadata: Optional extra context (top_k, filters, etc.).

        Returns:
            Completed Task object with search results in artifacts.
        """
        params = TaskSendParams(
            message=Message.user(query),
            metadata=metadata or {},
        )

        logger.info("a2a_task_sending", query_length=len(query), agent=self.base_url)

        response = await self._http.post(
            "/tasks",
            content=params.model_dump_json(),
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()

        task = Task(**response.json())
        logger.info("a2a_task_received", task_id=task.id, status=task.status)
        return task

    async def get_task(self, task_id: str) -> Task:
        """Poll for task status (useful for long-running tasks).

        Args:
            task_id: The task UUID.

        Returns:
            Updated Task object.
        """
        response = await self._http.get(f"/tasks/{task_id}")
        response.raise_for_status()
        return Task(**response.json())

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.aclose()

    async def __aenter__(self) -> "A2AClient":
        return self

    async def __aexit__(self, *_) -> None:
        await self.close()