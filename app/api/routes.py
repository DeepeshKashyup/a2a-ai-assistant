
import structlog
from fastapi import APIRouter
from pydantic import BaseModel

from src.utils.llm_client import LLMClient
from src.prompts.templates import PromptTemplateManager
import json
from fastapi.responses import StreamingResponse
logger = structlog.get_logger()
router = APIRouter()

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

@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """Direct chat with LLM - No Retrieval, No A2A."""
    logger.info("chat request", message_length=len(request.message), session_id=request.session_id)
    rendered_prompt = _prompts.render_chat(request.message)
    reply = await _llm.generate(rendered_prompt)
    return ChatResponse(
        reply=reply, 
        model=_llm.model_name, 
        session_id=request.session_id
    )

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