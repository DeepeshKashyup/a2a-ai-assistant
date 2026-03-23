
import json

import structlog
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agents.main_agent import MainAgent
from src.prompts.templates import PromptTemplateManager
from src.utils.llm_client import LLMClient

logger = structlog.get_logger()
router = APIRouter()

_main_agent = MainAgent()

# -- Schemas --------------------------------------------------

class HealthResponse(BaseModel):
    """ Health check response. """
    status: str
    version: str
    agent: str

class VersionResponse(BaseModel):
    """ Build info response. """
    version: str

class ChatRequest(BaseModel):
    """ Chat request schema. """
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    """ Chat response schema. """
    reply: str
    model: str
    session_id: str | None = None

class QueryRequest(BaseModel):
    """ Query request schema. """
    question: str
    session_id: str | None = None
    top_k: int = 5

class SourceItem(BaseModel):
    source_file: str
    score: float

class QueryResponse(BaseModel):
    """ Query response schema. """
    answer: str
    sources: list[SourceItem]
    model: str
    task_id: str
    latency_ms: float

# -- Routes ---------------------------------------------------

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """ Health check - confirms the main agent is running. """
    from app.core.config import settings
    logger.info("health check requested")
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        agent="main-agent"
    )

@router.get("/version", response_model=VersionResponse, tags=["System"])
async def version() -> VersionResponse:
    """ Returns the build info of the main agent. """
    from app.core.config import settings
    logger.info("version check requested")
    return VersionResponse(version=settings.app_version)

_llm = LLMClient()
_prompts = PromptTemplateManager()

@router.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream chat responses from LLM - No Retrieval, No A2A."""
    logger.info("streaming chat request", message_length=len(request.message), session_id=request.session_id)
    rendered_prompt = _prompts.render_chat(request.message)
    
    async def event_generator():
        async for chunk in _llm._client.astream(rendered_prompt):
            text = getattr(chunk, "content", "") or ""
            if text:
                yield f"data: {json.dumps({'token': text})}\n\n"
            
        yield f"data: {json.dumps({'done': True, 'model': _llm.model_name})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


from src.guardrails.input_guard import InputGuard
from src.guardrails.output_guard import OutputGuard

_input_guard = InputGuard()
_output_guard = OutputGuard()

# Replace the chat endpoint above with this guarded version:
@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_guarded(request: ChatRequest) -> ChatResponse:
    """Chat with input/output guardrails applied."""
    _input_guard.validate(request.message)
    prompt = _prompts.render_chat(question=request.message)
    reply = await _llm.generate(prompt)
    safe_reply = _output_guard.filter(reply)
    return ChatResponse(reply=safe_reply, model=_llm.model_name, session_id=request.session_id)


@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_guarded(request: QueryRequest) -> QueryResponse:
    """RAG query with input/output guardrails applied."""
    _input_guard.validate(request.question)
    result = await _main_agent.handle_query(question=request.question, top_k=request.top_k)
    safe_answer = _output_guard.filter(result["answer"])
    return QueryResponse(
        answer=safe_answer,
        sources=result["sources"],
        model=result["model"],
        task_id=result.get("task_id"),
    )