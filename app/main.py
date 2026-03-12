from contextlib import asynccontextmanager
from pathlib import Path

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import router

STATIC_DIR = Path(__file__).parent / "static"

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

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router, prefix="/api/v1")

@app.get("/ui", include_in_schema=False)
async def ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "ui.html")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)