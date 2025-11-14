import pytest
from unittest.mock import MagicMock, patch

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


@pytest.mark.asyncio
async def test_get_all_questions(mock_session, mock_question_model):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_question_model]
    mock_session.execute.return_value = mock_result

    result = await get_all_questions(mock_session)

    mock_session.execute.assert_called_once()
    assert len(result) == 1
    assert result[0].text == "Test question"


@pytest.mark.asyncio
async def test_get_question_with_answers_found(mock_session, mock_question_model):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_question_model
    mock_session.execute.return_value = mock_result

    result = await get_question_with_answers(mock_session, 1)

    mock_session.execute.assert_called_once()
    assert result == mock_question_model


@pytest.mark.asyncio
async def test_get_question_with_answers_not_found(mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await get_question_with_answers(mock_session, 999)

    assert result is None


@pytest.mark.asyncio
async def test_create_question(mock_session, mock_question_model):
    question_data = QuestionCreate(text="New question")

    new_question = MagicMock()
    new_question.id = 1

    final_result = MagicMock()
    final_result.scalar_one.return_value = mock_question_model

    mock_session.execute.return_value = final_result

    with patch("src.services.questions_answers.Question", return_value=new_question):
        with patch("src.services.questions_answers.select") as mock_select:
            with patch("src.services.questions_answers.selectinload") as mock_selectinload:
                mock_select.return_value.options.return_value.where.return_value = (
                    mock_select.return_value
                )
                mock_selectinload.return_value = None

                result = await create_question(mock_session, question_data)

    mock_session.add.assert_called_once_with(new_question)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(new_question, attribute_names=["answers"])
    mock_session.execute.assert_called_once()
    assert result == mock_question_model


@pytest.mark.asyncio
async def test_create_question_database_error(mock_session):
    question_data = QuestionCreate(text="New question")
    new_question = MagicMock()

    mock_session.commit.side_effect = Exception("Database connection error")

    with patch("src.services.questions_answers.Question", return_value=new_question):
        with patch("src.services.questions_answers.select"):
            with patch("src.services.questions_answers.selectinload"):
                with pytest.raises(Exception, match="Database connection error"):
                    await create_question(mock_session, question_data)

    mock_session.add.assert_called_once_with(new_question)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_not_called()
    mock_session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_delete_question_found(mock_session, mock_question_model):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_question_model
    mock_session.execute.return_value = mock_result

    result = await delete_question(mock_session, 1)

    mock_session.execute.assert_called_once()
    mock_session.delete.assert_called_once_with(mock_question_model)
    mock_session.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_question_not_found(mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await delete_question(mock_session, 999)

    mock_session.execute.assert_called_once()
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    assert result is False


@pytest.mark.asyncio
async def test_create_answer_success(mock_session, mock_question_model, mock_answer_model):
    answer_data = AnswerCreate(user_id="user_1", text="Test answer")

    question_result = MagicMock()
    question_result.scalar_one_or_none.return_value = mock_question_model

    mock_session.execute.return_value = question_result

    with patch("src.services.questions_answers.Answer", return_value=mock_answer_model):
        result = await create_answer(mock_session, 1, answer_data)

    mock_session.execute.assert_called_once()

    mock_session.add.assert_called_once_with(mock_answer_model)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_answer_model)

    assert result == mock_answer_model


@pytest.mark.asyncio
async def test_create_answer_question_not_found(mock_session):
    answer_data = AnswerCreate(user_id="user_1", text="Test answer")

    question_result = MagicMock()
    question_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = question_result

    result = await create_answer(mock_session, 999, answer_data)

    mock_session.execute.assert_called_once()
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    assert result is None


@pytest.mark.asyncio
async def test_create_answer_database_error(mock_session, mock_question_model):
    answer_data = AnswerCreate(user_id="user_1", text="Test answer")

    question_result = MagicMock()
    question_result.scalar_one_or_none.return_value = mock_question_model
    mock_session.execute.return_value = question_result

    mock_session.commit.side_effect = Exception("Database error")

    with patch("src.services.questions_answers.Answer"):
        with patch("src.services.questions_answers.select"):
            with pytest.raises(Exception, match="Database error"):
                await create_answer(mock_session, 1, answer_data)

    mock_session.execute.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_get_answer_found(mock_session, mock_answer_model):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_answer_model
    mock_session.execute.return_value = mock_result

    result = await get_answer(mock_session, 1)

    mock_session.execute.assert_called_once()
    assert result == mock_answer_model


@pytest.mark.asyncio
async def test_get_answer_not_found(mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await get_answer(mock_session, 999)

    assert result is None


@pytest.mark.asyncio
async def test_delete_answer_found(mock_session, mock_answer_model):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_answer_model
    mock_session.execute.return_value = mock_result

    result = await delete_answer(mock_session, 1)

    mock_session.execute.assert_called_once()
    mock_session.delete.assert_called_once_with(mock_answer_model)
    mock_session.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_answer_not_found(mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await delete_answer(mock_session, 999)

    mock_session.execute.assert_called_once()
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    assert result is False
