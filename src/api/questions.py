from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import JSONResponse
from src.services.questions_answers import (
    get_all_questions,
    create_question,
    get_question_with_answers,
    delete_question,
)
from src.schemas.questions_answers import QuestionCreate, QuestionRead
from src.core.db_config import db_dependency

questions_router = APIRouter(prefix="/questions", tags=["Questions"])


@questions_router.get(
    "/", response_model=list[QuestionRead], summary="Получить список всех вопросов"
)
async def list_questions(db: db_dependency):
    try:
        questions = await get_all_questions(db)
        return questions
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})


@questions_router.post(
    "/",
    response_model=QuestionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать вопрос",
)
async def new_question(question: QuestionCreate, db: db_dependency):
    try:
        db_question = await create_question(db, question)
        return db_question
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": 500, "message": str(e), "id": None},
        )


@questions_router.get(
    "/{question_id}",
    response_model=QuestionRead,
    summary="Получить вопрос по id",
    description="Получить вопрос по id со всеми ответами на него",
)
async def get_question(question_id: int, db: db_dependency):
    try:
        question = await get_question_with_answers(db, question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Вопрос не найден")
        return question
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})


@questions_router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить вопрос по id c ответами",
    description="Удалить вопрос по id со всеми ответами на него",
)
async def remove_question(question_id: int, db: db_dependency):
    try:
        await delete_question(db, question_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})
