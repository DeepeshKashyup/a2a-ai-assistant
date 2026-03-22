"""Main Agent - Orchestrates A2A calls to the content search agent and LLM synthesis."""

# =====================================================================================================================
# Main Agent
# =====================================================================================================================

import structlog
import time
from src.a2a.client import A2AClient
from src.a2a.protocol import Task, Message, AgentCard
from src.prompts.templates import PromptTemplateManager
from src.utils.llm_client import LLMClient
from src.a2a.protocol import TaskStatus
from src.utils.helpers import elapsed_ms

logger = structlog.get_logger()

class MainAgent:
    """
    Orchestrates the full query flow:
        1. Receives a user query.
        2. Sends the query to the Content Search Agent.
        3. Retrieves retrieved document chunks as artifacts.
        4. Constructs a grounded prompt and calls Gemini for synthesis.
        5. Returns the synthesized answer with source citations.
    """

    def __init__(self) -> None:
        self._llm = LLMClient()
        self._a2a = A2AClient()
        self._prompts = PromptTemplateManager()
        logger.info("main_agent_initialized")

    async def handle_query(self, query: str, top_k: int = 5) -> dict:
        """End-to-end query handling: search -> synthesize -> respond.
        
        Args:
            query: The user's natural language question.
            top_k: Number of search results to retrieve from the Search Agent.
        
        Returns:
            Dict with keys: answer, sources, model, task_id, latency_ms.
        """
        start = time.time()
        logger.info("main_agent_query", query_length=len(query), top_k=top_k)

        # Step 1: Send query to Search Agent
        task = await self._a2a.send_task(
            query, 
            metadata={"top_k": top_k}
        )

        if task.status != TaskStatus.COMPLETED:
            logger.error("search task failed", task_id=task.id, status=task.status)
            return {"error": f"Search Agent task failed with status {task.status}"}
        
        # Step 2: Extract retrieved chunks from task artifacts
        artifacts = task.artifacts or []
        if not artifacts:
            logger.warn("no_artifact_retuned", task_id=task.id)
            context = "No relevant documents found."
            sources = []
        else:
            context = self._build_context(artifacts)
            sources = [
                {
                    "source_file" : a.get("source_file", "unknown"),
                    "score" : a.get("score", 0),
                }
                for a in artifacts
            ]
        
        # Step 3: Synthesize answer using Gemini flash with retrieval context

        answer = await self._llm.generate_with_context(
            question=query, 
            context=context,
            system=self._prompts.system_prompt,
        )

        latency = elapsed_ms(start)
        logger.info("main_agent_done", task_id=task.id, latency_ms=latency, sources=len(sources))

        return {
            "answer": answer,
            "sources": sources,
            "model": self._llm.model_name,
            "task_id": task.id,
            "latency_ms": latency,
        }


    def _build_context(self, artifacts: list[dict]) -> str:
        """Format retrieved chunks into a single context string for the LLM."""
        # For simplicity, we concatenate the top-k chunks with their source info.
        # In a real implementation, we might want to format this more nicely or include metadata.
        context_parts = []
        for i, artifact in enumerate(artifacts):
            text = artifact.get("text", "")
            source = artifact.get("source_file", "unknown")
            score = artifact.get("score", 0)
            context_parts.append(f"[{i}] Source: {source} (relevance: {score:.2f})\\n{text}")
        
        return "\n".join(context_parts)
