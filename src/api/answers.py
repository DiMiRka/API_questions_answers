from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import JSONResponse
from src.core.db_config import db_dependency
from src.schemas.questions_answers import AnswerRead, AnswerCreate
from src.services.questions_answers import (
    create_answer,
    get_answer,
    delete_answer,
    get_question_with_answers,
)


answers_router = APIRouter(prefix="/answers", tags=["Answers"])


@answers_router.post(
    "/question/{question_id}",
    response_model=AnswerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить ответ к вопросу",
)
async def post_answer(db: db_dependency, question_id: int, answer: AnswerCreate):
    try:
        question = await get_question_with_answers(db, question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Вопрос не найден")

        db_answer = await create_answer(db, question_id, answer)
        return db_answer
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": 500, "message": str(e), "id": None},
        )


@answers_router.get("/{answer_id}", response_model=AnswerRead, summary="Получить ответ по id")
async def get_answer_by_id(db: db_dependency, answer_id: int):
    try:
        answer = await get_answer(db, answer_id)
        if not answer:
            raise HTTPException(status_code=404, detail="Ответ не найден")
        return answer
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})


@answers_router.delete("/{answer_id}", summary="Удалить ответ")
async def delete_answer_by_id(db: db_dependency, answer_id: int):
    try:
        result = await delete_answer(db, answer_id)
        if not result:
            raise HTTPException(status_code=404, detail="Ответ не найден")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})
