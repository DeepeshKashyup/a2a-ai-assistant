"""Content Search Agent logic - perform vector similarity search on request

This modules contains the core search logic. The FastAPI app that exposes
it via A2A endpoints lives in search_agent_app/.

# ==========================================================================
# Content Search Agent Logic
# ==========================================================================

"""

import structlog
import time

from src.utils.helpers import elapsed_ms

logger = structlog.get_logger()
from src.retrieval.vectorstore import SearchResult, VectorStore
from src.a2a.protocol import TaskSendParams, TaskStatus, Task

class ContentSearchAgent:
    """
    Content Search Agent - the core A2A-capable search service.

    Responsibilities:
        - Receive a search task (query string) via A2A protocol.
        - Perform vector similary search in ChromaDB
        - Return ranked document chunks as task artifacts.
        - Report task status back to the caller
    """

    AGENT_NAME = "Content Search Agent"
    AGENT_VERSION = "0.1.0"
    AGENT_DESCRIPTION = (
        "Retrieves relevant document chunks from the in-house knowledge base "
        "using vector similarity search (Vertex AI text-embedding-004 + ChromaDB)."
    )

    def __init__(self) -> None:
        self._vectorstore = VectorStore()
        logger.info("search_agent_initialized", collection_size=self._vectorstore.count)

    async def process_task(self, params: TaskSendParams) -> Task:
        """Process an incoming A2A search task.
        
        Extracts the query from the task message, runs vector search,
        and returns a completed Task with results as artifacts.

        Args:
            params: TaskSendParams containing the user query message.

        Returns:
            Completed Task with search results in artifacts.        
        """

        start = time.time()
        task = Task(id=params.id, messages=[params.message], status=TaskStatus.WORKING)

        query = params.message.text
        logger.info("search_task_started", task_id=task.id, query_length=len(query))

        try:
            results: list[SearchResult] = self._vectorstore.search(query=query)
            artifacts = [
                {
                    "chunk_id": r.chunk_id,
                    "text": r.text,
                    "score": r.score,
                    "source_file": r.source_file,
                    "chunk_index": r.chunk_index,
                }
                for r in results
            ]

            reply = f"Found {len(artifacts)} relevant document chunks.'{query[:80]}...'"
            task.complete(reply_text=reply, artifacts=artifacts)
            logger.info(
                "search_task_completed",
                task_id=task.id,
                num_results=len(artifacts),
                latency_ms=elapsed_ms(start),
            )
        except Exception as e:
            logger.error("search_task_failed", task_id=task.id, error=str(e))
            task.fail(reason=str(e))

        return task
    
    def get_agent_card_data(self, base_url: str) -> dict:
        """Return the data needed to build the Agent's A2A card."""
        return {
            "name": self.AGENT_NAME,
            "description": self.AGENT_DESCRIPTION,
            "url": base_url,
            "version": self.AGENT_VERSION,
            "capabilities": {
                "streaming": False,
                "push notifications": False,
                "state_transition_history": False,
            },
            "skills": [
                {
                    "id": "semantic_search",
                    "name": "Semantic Document Search",
                    "description": "Search in-house documents using natural language queries",
                    "input_modes": ["text"],
                    "output_modes": ["text"],
                }
            ]
        }