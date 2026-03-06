from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import router

setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Startup and shutdown lifecycle."""
    logger.info(
        "main agent starting",
        app=settings.app_name,
        version=settings.app_version,
        env=settings.env,
        port=settings.port,
    )
    
    yield

    logger.info("main agent stopping", app=settings.app_name)

app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api/v1")