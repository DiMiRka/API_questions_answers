from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from src.models.questions_answers import Question, Answer
from src.schemas.questions_answers import QuestionCreate, AnswerCreate


async def get_all_questions(db: AsyncSession) -> List[Question]:
    result = await db.execute(select(Question).options(selectinload(Question.answers)))
    return list(result.scalars().all())


async def get_question_with_answers(db: AsyncSession, question_id: int) -> Optional[Question]:
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.answers))
        .where(Question.id == question_id)
    )
    return result.scalar_one_or_none()


async def create_question(db: AsyncSession, question: QuestionCreate) -> Question:
    new_question = Question(text=question.text)
    db.add(new_question)
    await db.commit()
    await db.refresh(new_question, attribute_names=["answers"])
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.answers))
        .where(Question.id == new_question.id)
    )
    db_question = result.scalar_one()
    return db_question


async def delete_question(db: AsyncSession, question_id: int) -> bool:
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        return False

    await db.delete(question)
    await db.commit()
    return True


async def create_answer(
    db: AsyncSession, question_id: int, answer: AnswerCreate
) -> Optional[Answer]:

    q_result = await db.execute(select(Question).where(Question.id == question_id))
    question = q_result.scalar_one_or_none()
    if not question:
        return None

    new_answer = Answer(question_id=question_id, user_id=answer.user_id, text=answer.text)
    db.add(new_answer)
    await db.commit()
    await db.refresh(new_answer)
    return new_answer


async def get_answer(db: AsyncSession, answer_id: int) -> Optional[Answer]:
    result = await db.execute(select(Answer).where(Answer.id == answer_id))
    return result.scalar_one_or_none()


async def delete_answer(db: AsyncSession, answer_id: int) -> bool:
    result = await db.execute(select(Answer).where(Answer.id == answer_id))
    answer = result.scalar_one_or_none()
    if not answer:
        return False

    await db.delete(answer)
    await db.commit()
    return True
