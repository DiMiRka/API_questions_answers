from unittest.mock import MagicMock, patch

import pytest

from src.models.questions_answers import Question
from src.schemas.questions_answers import QuestionCreate, AnswerCreate
from src.services.questions_answers import (
    get_all_questions,
    get_question_with_answers,
    create_question,
    delete_question,
    create_answer,
    get_answer,
    delete_answer,
)


def make_scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    result.scalar_one.return_value = value
    result.scalars.return_value.all.return_value = [value] if value else []
    return result


@pytest.mark.asyncio
async def test_get_all_questions(mock_session, mock_question_model):
    mock_session.execute.return_value = make_scalar_result(mock_question_model)

    result = await get_all_questions(mock_session)

    mock_session.execute.assert_called_once()
    assert len(result) == 1
    assert result[0] == mock_question_model


@pytest.mark.asyncio
async def test_get_question_with_answers_found(mock_session, mock_question_model):
    mock_session.execute.return_value = make_scalar_result(mock_question_model)

    result = await get_question_with_answers(mock_session, 1)

    mock_session.execute.assert_called_once()
    assert result == mock_question_model


@pytest.mark.asyncio
async def test_get_question_with_answers_not_found(mock_session):
    mock_session.execute.return_value = make_scalar_result(None)

    result = await get_question_with_answers(mock_session, 999)

    assert result is None


@pytest.mark.asyncio
async def test_create_question(mock_session, mock_question_model):
    async def test_create_question(mock_session, mock_question_model):
        payload = QuestionCreate(text="New question")

        new_question = Question(text="New question")
        new_question.id = 1

        mock_session.execute.return_value = make_scalar_result(mock_question_model)

        with patch(
            "src.services.questions_answers.Question",
            side_effect=lambda **kwargs: new_question,
        ):
            result = await create_question(mock_session, payload)

        mock_session.add.assert_called_once_with(new_question)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(
            new_question, attribute_names=["answers"]
        )
        assert result == mock_question_model


@pytest.mark.asyncio
async def test_create_question_database_error(mock_session):
    payload = QuestionCreate(text="New question")
    new_question = Question(text="New question")

    mock_session.commit.side_effect = Exception("Database connection error")

    with patch("src.services.questions_answers.Question", return_value=new_question):
        with pytest.raises(Exception, match="Database connection error"):
            await create_question(mock_session, payload)

    mock_session.add.assert_called_once_with(new_question)
    mock_session.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_delete_question_found(mock_session, mock_question_model):
    mock_session.execute.return_value = make_scalar_result(mock_question_model)

    result = await delete_question(mock_session, 1)

    mock_session.execute.assert_called_once()
    mock_session.delete.assert_called_once_with(mock_question_model)
    mock_session.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_question_not_found(mock_session):
    mock_session.execute.return_value = make_scalar_result(None)

    result = await delete_question(mock_session, 999)

    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    assert result is False


@pytest.mark.asyncio
async def test_create_answer_success(mock_session, mock_question_model, mock_answer_model):
    payload = AnswerCreate(user_id="u1", text="hello")

    mock_session.execute.return_value = make_scalar_result(mock_question_model)

    with patch("src.services.questions_answers.Answer", return_value=mock_answer_model):
        result = await create_answer(mock_session, 1, payload)

    mock_session.add.assert_called_once_with(mock_answer_model)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_answer_model)
    assert result == mock_answer_model


@pytest.mark.asyncio
async def test_create_answer_question_not_found(mock_session):
    payload = AnswerCreate(user_id="u1", text="hello")

    mock_session.execute.return_value = make_scalar_result(None)

    result = await create_answer(mock_session, 999, payload)

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    assert result is None


@pytest.mark.asyncio
async def test_create_answer_database_error(mock_session, mock_question_model):
    payload = AnswerCreate(user_id="u1", text="hello")

    mock_session.execute.return_value = make_scalar_result(mock_question_model)
    mock_session.commit.side_effect = Exception("Database error")

    from src.services.questions_answers import Answer as AnswerModel

    AnswerModel.__call__ = MagicMock()

    with pytest.raises(Exception, match="Database error"):
        await create_answer(mock_session, 1, payload)

    mock_session.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_get_answer_found(mock_session, mock_answer_model):
    mock_session.execute.return_value = make_scalar_result(mock_answer_model)

    result = await get_answer(mock_session, 1)

    assert result == mock_answer_model


@pytest.mark.asyncio
async def test_get_answer_not_found(mock_session):
    mock_session.execute.return_value = make_scalar_result(None)

    result = await get_answer(mock_session, 999)

    assert result is None


@pytest.mark.asyncio
async def test_delete_answer_found(mock_session, mock_answer_model):
    mock_session.execute.return_value = make_scalar_result(mock_answer_model)

    result = await delete_answer(mock_session, 1)

    mock_session.delete.assert_called_once_with(mock_answer_model)
    mock_session.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_answer_not_found(mock_session):
    mock_session.execute.return_value = make_scalar_result(None)

    result = await delete_answer(mock_session, 999)

    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    assert result is False
