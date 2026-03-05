
import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = structlog.get_logger()
router = APIRouter()

# -- Schemas --------------------------------------------------

class HealthResponse(BaseModel):
    """ Health check response. """
    status: str
    version: str
    agent: str


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