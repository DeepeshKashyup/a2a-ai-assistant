"""A2A endpoint routes for the content search agent.

Implements the A2A protocol:
    GET /.well-known/agent.json → agent capbility card
    POST /tasks                 → submit a search task
    GET /tasks/{task_id}        → retrieve task status and results

# =====================================================
# Search Agent A2A Routes
# =====================================================
"""

import structlog
from fastapi import APIRouter, HTTPException, Request
from src.a2a.protocol import AgentCard, Task, TaskSendParams, AgentSkill
from src.agents.search_agent import ContentSearchAgent
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()

_search_agent = ContentSearchAgent()
_task_store: dict[str, Task] = {}  # In-memory store, replace with redis for production

@router.get("/.well-known/agent.json", response_model=AgentCard, tags=["A2A"])
async def get_agent_card(request: Request) -> AgentCard:
    """Return the agent's capability card (A2A discovery endpoint)."""
    base_url = str(request.base_url).rstrip("/")
    card_data = _search_agent.get_agent_card_data(base_url=base_url)
    return AgentCard(**card_data)

@router.post("/tasks", response_model=Task, tags=["A2A"])
async def submit_task(params: TaskSendParams) -> Task:
    """Submit a new search task to the Content Search Agent.
    
    The agent immediately processes the task (synchronous) and returns
    the completed Task with search results as artifacts.

    Args:
        params: TaskSendParams containing the search query message.

    Returns:
        Completed Task with retrieved document chunks in artifacts.
    """
    logger.info("task received", task_id=params.id, query = params.message.text[:80])
    task = await _search_agent.process_task(params)
    _task_store[task.id] = task
    return task

@router.get("/tasks/{task_id}", response_model=Task, tags=["A2A"])
async def get_task(task_id: str) -> Task:
    """Retrieve a task by ID (for polling long running tasks).
    
    Args:
        task_id: The UUID of the task to retrieve.

    Returns:
        The Task object with current status and messages (if completed).
    
    """
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/health", tags=["System"])
async def health_check() -> dict:
    """Health check for the search agent."""
    return {
        "status": "ok",
        "agent": ContentSearchAgent.AGENT_NAME,
        "collection_size": _search_agent._vectorstore.count,
    }