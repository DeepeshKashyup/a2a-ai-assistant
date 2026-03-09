
import structlog
from fastapi import APIRouter
from pydantic import BaseModel

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