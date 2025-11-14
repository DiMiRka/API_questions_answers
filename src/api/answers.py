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
from src.core.logging import get_logger

logger = get_logger("questions_answers.api.answers")

answers_router = APIRouter(prefix="/answers", tags=["Answers"])


@answers_router.post(
    "/question/{question_id}",
    response_model=AnswerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить ответ к вопросу",
)
async def post_answer(db: db_dependency, question_id: int, answer: AnswerCreate):
    try:
        logger.info(
            f"POST/answers/question/{question_id} Создаем ответ к вопросу с ID {question_id}"
        )
        question = await get_question_with_answers(db, question_id)
        if not question:
            logger.warning(
                f"POST/answers/question/{question_id} Вопрос с ID {question_id} не найден"
            )
            raise HTTPException(status_code=404, detail="Вопрос не найден")

        db_answer = await create_answer(db, question_id, answer)
        logger.info(
            f"POST/answers/question/{question_id} Успешно создан ответ с ID {db_answer.id}"
        )
        return db_answer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"POST/answers/question/{question_id} Ошибка: {str(e)}", exc_info=True)
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": 500, "message": str(e), "id": None},
        )


@answers_router.get("/{answer_id}", response_model=AnswerRead, summary="Получить ответ по id")
async def get_answer_by_id(db: db_dependency, answer_id: int):
    try:
        logger.info(f"GET/answers/{answer_id} Получаем ответ с ID {answer_id}")
        answer = await get_answer(db, answer_id)
        if not answer:
            logger.warning(f"GET/answers/{answer_id} Ответ с ID {answer_id} не найден")
            raise HTTPException(status_code=404, detail="Ответ не найден")
        logger.info(f"GET/answers/{answer_id} Успешно получен ответ с ID {answer_id}")
        return answer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GET/answers/{answer_id} Ошибка: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})


@answers_router.delete("/{answer_id}", summary="Удалить ответ")
async def delete_answer_by_id(db: db_dependency, answer_id: int):
    try:
        logger.info(f"DELETE/answers/{answer_id} Удаляем ответ с ID {answer_id}")
        result = await delete_answer(db, answer_id)
        if not result:
            logger.warning(f"DELETE/answers/{answer_id} Ответ с ID {answer_id} не найден")
            raise HTTPException(status_code=404, detail="Ответ не найден")
        logger.info(f"DELETE/answers/{answer_id} Успешно удален ответ с ID {answer_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DELETE/answers/{answer_id} Ошибка: {str(e)}", exc_info=True)
        await db.rollback()
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})
