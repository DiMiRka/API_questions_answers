import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.questions_answers import (
    get_all_questions,
    get_question_with_answers,
    create_question,
    delete_question,
    create_answer,
    get_answer,
    delete_answer,
)
from src.schemas.questions_answers import QuestionCreate, AnswerCreate
from src.models.questions_answers import Question, Answer


@pytest.mark.asyncio
async def test_get_all_questions():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_question = MagicMock()
    mock_question.id = 1
    mock_question.text = "Test question"

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_question]
    mock_session.execute.return_value = mock_result

    result = await get_all_questions(mock_session)

    assert len(result) == 1
    assert result[0].text == "Test question"


@pytest.mark.asyncio
async def test_create_question():
    mock_session = AsyncMock(spec=AsyncSession)
    question_data = QuestionCreate(text="New question")

    mock_question = MagicMock()
    mock_question.id = 1
    mock_question.text = "New question"

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = mock_question
    mock_session.execute.return_value = mock_result

    result = await create_question(mock_session, question_data)

    assert result.text == "New question"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
