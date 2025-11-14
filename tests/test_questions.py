import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.schemas.questions_answers import QuestionRead


@pytest.mark.asyncio
async def test_create_question(test_client: AsyncClient):
    question_data = QuestionRead(
        id=1, text="Как тебя зовут?", created_at=datetime.now(), answers=[]
    )

    with patch(
        "src.api.questions.create_question", new=AsyncMock(return_value=question_data)
    ):
        response = await test_client.post("/questions/", json={"text": "Как тебя зовут?"})

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Как тебя зовут?"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_all_questions(test_client: AsyncClient):
    question1 = QuestionRead(id=1, text="Вопрос 1", created_at=datetime.now(), answers=[])
    question2 = QuestionRead(id=2, text="Вопрос 2", created_at=datetime.now(), answers=[])

    with patch(
        "src.api.questions.get_all_questions",
        new=AsyncMock(return_value=[question1, question2]),
    ):
        response = await test_client.get("/questions/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["text"] == "Вопрос 1"
    assert data[1]["text"] == "Вопрос 2"


@pytest.mark.asyncio
async def test_get_question_by_id(test_client: AsyncClient):
    question_data = QuestionRead(
        id=1, text="Что нового?", created_at=datetime.now(), answers=[]
    )

    with patch(
        "src.api.questions.get_question_with_answers",
        new=AsyncMock(return_value=question_data),
    ):
        response = await test_client.get("/questions/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["text"] == "Что нового?"


@pytest.mark.asyncio
async def test_get_question_by_id_not_found(test_client: AsyncClient):
    with patch(
        "src.api.questions.get_question_with_answers", new=AsyncMock(return_value=None)
    ):
        response = await test_client.get("/questions/999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Вопрос не найден"


@pytest.mark.asyncio
async def test_delete_question(test_client: AsyncClient):
    with patch("src.api.questions.delete_question", new=AsyncMock(return_value=True)):
        response = await test_client.delete("/questions/1")

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_question_not_found(test_client: AsyncClient):
    with patch("src.api.questions.delete_question", new=AsyncMock(return_value=False)):
        response = await test_client.delete("/questions/999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Вопрос не найден"
