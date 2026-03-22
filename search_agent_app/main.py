"""Content Search Agent - standalone FastAPI app searving A2A endpoints.

Runs on port 8081 (configurable). The Main Agent calls this via HTTP
using the A2A protocol (src/a2a/client.py).

# ==================================================================
# Search Agent App
# ==================================================================
"""

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from search_agent_app.routes import router

setup_logging()
logger = structlog.get_logger()

app = FastAPI(
    title="Content Search Agent",
    description="A2A-compatible semantic search agent over in-house documents.",
    version="0.1.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup_event() -> None:
    logger.info(
        "search_agent_starting",
        port=settings.search_agent_port,
        agent_url=settings.search_agent_url,
    )

@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("search_agent_shutting_down")

if __name__ == "__main__":
    uvicorn.run(
        "search_agent_app.main:app",
        host="0.0.0.0",
        port=settings.search_agent_port,
        reload=settings.debug,
        log_level="info",
    )