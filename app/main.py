from fastapi import FastAPI
import structlog
from contextlib import asynccontextmanager
from app.core.logging import setup_logging
from app.core.config import settings

def fake_answer_to_everything_ml_model(x:float):
    return x*42


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

""" @app.get("/predict/{x}")
async def predict(x:float):
    result = ml_model["answer to everything"](x)
    return {"result": result}

@app.get("/")
async def root():
    return {"message": "Hello"}


@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id} """