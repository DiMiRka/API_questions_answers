import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.schemas.questions_answers import AnswerRead, QuestionRead


@pytest.mark.asyncio
async def test_create_answer(test_client: AsyncClient):
    question_mock = QuestionRead(
        id=1, text="Тестовый вопрос", created_at=datetime.now(), answers=[]
    )
    answer_data = AnswerRead(
        id=1, question_id=1, user_id="user_1", text="Тест", created_at=datetime.now()
    )

    with patch(
        "src.api.answers.get_question_with_answers", new=AsyncMock(return_value=question_mock)
    ):
        with patch("src.api.answers.create_answer", new=AsyncMock(return_value=answer_data)):
            response = await test_client.post(
                "/answers/question/1", json={"user_id": "user_1", "text": "Тест"}
            )

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Тест"
    assert data["question_id"] == 1


@pytest.mark.asyncio
async def test_create_answer_question_not_found(test_client: AsyncClient):
    with patch("src.api.answers.get_question_with_answers", new=AsyncMock(return_value=None)):
        response = await test_client.post(
            "/answers/question/999", json={"user_id": "user_1", "text": "Тест"}
        )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Вопрос не найден"


@pytest.mark.asyncio
async def test_get_answer_by_id(test_client: AsyncClient):
    answer_data = AnswerRead(
        id=1, question_id=1, user_id="user_2", text="Среда", created_at=datetime.now()
    )

    with patch("src.api.answers.get_answer", new=AsyncMock(return_value=answer_data)):
        response = await test_client.get("/answers/1")

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Среда"
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_get_answer_by_id_not_found(test_client: AsyncClient):
    with patch("src.api.answers.get_answer", new=AsyncMock(return_value=None)):
        response = await test_client.get("/answers/999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Ответ не найден"


@pytest.mark.asyncio
async def test_delete_answer(test_client: AsyncClient):
    with patch("src.api.answers.delete_answer", new=AsyncMock(return_value=True)):
        response = await test_client.delete("/answers/1")

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_answer_not_found(test_client: AsyncClient):
    with patch("src.api.answers.delete_answer", new=AsyncMock(return_value=False)):
        response = await test_client.delete("/answers/999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Ответ не найден"
