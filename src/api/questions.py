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
from src.core.logging import get_logger

logger = get_logger("questions_answers.api.questions")
questions_router = APIRouter(prefix="/questions", tags=["Questions"])


@questions_router.get(
    "/", response_model=list[QuestionRead], summary="Получить список всех вопросов"
)
async def list_questions(db: db_dependency):
    try:
        logger.info("GET/questions Получаем список всех вопросов")
        questions = await get_all_questions(db)
        logger.info(f"GET/questions Успешно получено {len(questions)} вопросов")
        return questions
    except Exception as e:
        logger.error(f"GET/questions Ошибка: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})


@questions_router.post(
    "/",
    response_model=QuestionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать вопрос",
)
async def new_question(question: QuestionCreate, db: db_dependency):
    try:
        logger.info(f"POST/questions Создаем вопрос: {question.text[:25]}...")
        db_question = await create_question(db, question)
        logger.info(f"POST/questions Успешно создан вопрос с ID {db_question.id}")
        return db_question
    except Exception as e:
        logger.error(f"POST/questions Ошибка: {str(e)}", exc_info=True)
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
        logger.info(f"GET/questions/{question_id} Получаем вопрос с ID {question_id}")
        question = await get_question_with_answers(db, question_id)
        if not question:
            logger.warning(f"GET/questions/{question_id} Вопрос с ID {question_id} не найден")
            raise HTTPException(status_code=404, detail="Вопрос не найден")
        logger.info(f"GET/questions/{question_id} Успешно получен вопрос с ID {question_id}")
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GET/questions/{question_id} Ошибка: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})


@questions_router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить вопрос по id c ответами",
    description="Удалить вопрос по id со всеми ответами на него",
)
async def remove_question(question_id: int, db: db_dependency):
    try:
        logger.info(f"DELETE/questions/{question_id} Удаляем вопрос с ID {question_id}")
        result = await delete_question(db, question_id)
        if not result:
            logger.warning(
                f"DELETE/questions/{question_id} Вопрос с ID {question_id} не найден"
            )
            raise HTTPException(status_code=404, detail="Вопрос не найден")
        logger.info(
            f"DELETE/questions/{question_id} Успешно удален вопрос с ID {question_id}"
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DELETE/questions/{question_id} Ошибка: {str(e)}", exc_info=True)
        await db.rollback()
        return JSONResponse(status_code=500, content={"status": 500, "message": str(e)})
