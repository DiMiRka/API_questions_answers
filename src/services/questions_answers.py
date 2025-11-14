from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from src.models.questions_answers import Question, Answer
from src.schemas.questions_answers import QuestionCreate, AnswerCreate
from src.core.logging import get_logger

logger = get_logger('questions_answers.services')


async def get_all_questions(db: AsyncSession) -> List[Question]:
    logger.info("Получаем список всех вопросов")
    try:
        result = await db.execute(select(Question).options(selectinload(Question.answers)))
        questions = list(result.scalars().all())
        logger.info(f"Успешно получили {len(questions)} вопросов")
        return questions
    except Exception as e:
        logger.error(f"Ошибка при получении всех вопросов: {str(e)}")
        raise


async def get_question_with_answers(db: AsyncSession, question_id: int) -> Optional[Question]:
    logger.info(f"Получаем вопрос с ID {question_id}")
    try:
        result = await db.execute(
            select(Question)
            .options(selectinload(Question.answers))
            .where(Question.id == question_id)
        )
        question = result.scalar_one_or_none()
        if question:
            logger.info(f"Успешно получен вопрос с ID {question_id} и {len(question.answers)} ответами на него")
        else:
            logger.warning(f"Вопрос с ID {question_id} не найден")
        return question
    except Exception as e:
        logger.error(f"Ошибка при получении вопроса с ID {question_id}: {str(e)}")
        raise


async def create_question(db: AsyncSession, question: QuestionCreate) -> Question:
    logger.info(f"Создаем вопрос: {question.text[:25]}...")
    try:
        new_question = Question(text=question.text)
        db.add(new_question)
        await db.commit()
        await db.refresh(new_question, attribute_names=["answers"])
        result = await db.execute(
            select(Question)
            .options(selectinload(Question.answers))
            .where(Question.id == new_question.id)
        )
        created_question = result.scalar_one()
        logger.info(f"Успешно создан вопрос с ID {created_question.id}")
        return created_question
    except Exception as e:
        logger.error(f"Ошибка при создании вопроса: {str(e)}")
        await db.rollback()
        raise


async def delete_question(db: AsyncSession, question_id: int) -> bool:
    logger.info(f"Удаляем вопрос с ID {question_id}")
    try:
        result = await db.execute(select(Question).where(Question.id == question_id))
        question = result.scalar_one_or_none()
        if not question:
            logger.warning(f"Вопрос c ID {question_id} не найден")
            return False

        await db.delete(question)
        await db.commit()
        logger.info(f"Успешно удален вопрос с ID {question_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении вопроса с {question_id}: {str(e)}")
        raise


async def create_answer(
    db: AsyncSession, question_id: int, answer: AnswerCreate
) -> Optional[Answer]:
    logger.info(f"Создаем ответ для вопроса с ID {question_id}")
    try:
        q_result = await db.execute(select(Question).where(Question.id == question_id))
        question = q_result.scalar_one_or_none()
        if not question:
            logger.warning(f"Вопрос с ID {question_id} не найден при создании ответа")
            return None

        new_answer = Answer(question_id=question_id, user_id=answer.user_id, text=answer.text)
        db.add(new_answer)
        await db.commit()
        await db.refresh(new_answer)
        logger.info(f"Успешно создан ответ с ID {new_answer.id} для вопроса с ID {question_id}")
        return new_answer
    except Exception as e:
        logger.error(f"Ошибка при создании ответа к вопросу с ID {question_id}: {str(e)}")
        raise


async def get_answer(db: AsyncSession, answer_id: int) -> Optional[Answer]:
    logger.info(f"Получаем ответ с ID {answer_id}")
    try:
        result = await db.execute(select(Answer).where(Answer.id == answer_id))
        answer = result.scalar_one_or_none()
        if answer:
            logger.info(f"Успешно получен ответ с ID {answer_id}")
        else:
            logger.warning(f"Ответ с ID {answer_id} не найден")
        return answer
    except Exception as e:
        logger.error(f"Ошибка при получении ответа с ID {answer_id}: {str(e)}")
        raise


async def delete_answer(db: AsyncSession, answer_id: int) -> bool:
    logger.info(f"Удаляем ответ с ID {answer_id}")
    try:
        result = await db.execute(select(Answer).where(Answer.id == answer_id))
        answer = result.scalar_one_or_none()
        if not answer:
            logger.warning(f"Ответ с ID {answer_id} не найден для удаления")
            return False

        await db.delete(answer)
        await db.commit()
        logger.info(f"Успешно удален ответ с ID {answer_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении ответа с ID {answer_id}: {str(e)}")
        raise
