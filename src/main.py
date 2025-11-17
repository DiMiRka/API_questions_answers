from fastapi import FastAPI
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from src.core import uvicorn_options
from src.api import api_router
from src.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger("questions_answers.main")

env_path = Path(".") / (".env.docker" if os.getenv("DOCKER_MODE") else ".env")
load_dotenv(env_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения")
    yield
    logger.info("Отключение приложения")


app = FastAPI(
    title="API-сервис вопросов и ответов", docs_url="/api/openapi", lifespan=lifespan
)

app.include_router(api_router)


@app.get("/", tags=["root"])
async def root():
    return {"message": "API-сервис вопросов и ответов запущен"}


if __name__ == "__main__":
    uvicorn.run("main:app", **uvicorn_options)
