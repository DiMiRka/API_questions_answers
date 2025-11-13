from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

from src.core import uvicorn_options
from src.api import api_router

env_path = Path(".") / (".env.docker" if os.getenv("DOCKER_MODE") else ".env")
load_dotenv(env_path)

app = FastAPI(title="API-сервис вопросов и ответов", docs_url="/api/openapi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["root"])
async def root():
    return {"message": "API-сервис вопросов и ответов запущен"}


if __name__ == "__main__":
    uvicorn.run("main:app", **uvicorn_options)
