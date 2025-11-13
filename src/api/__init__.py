from fastapi import APIRouter
from src.api.questions import questions_router
from src.api.answers import answers_router

api_router = APIRouter()

api_router.include_router(questions_router)
api_router.include_router(answers_router)
