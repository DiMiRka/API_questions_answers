import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_create_question(test_client: AsyncClient, mock_question_read):
    with patch(
        "src.api.questions.create_question", new=AsyncMock(return_value=mock_question_read)
    ):
        response = await test_client.post("/questions/", json={"text": "Как тебя зовут?"})

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Test question"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_all_questions(test_client: AsyncClient, mock_questions_list):
    with patch(
        "src.api.questions.get_all_questions",
        new=AsyncMock(return_value=mock_questions_list),
    ):
        response = await test_client.get("/questions/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["text"] == "Test question"
    assert data[1]["text"] == "Second question"


@pytest.mark.asyncio
async def test_get_question_by_id(test_client: AsyncClient, mock_question_read):
    with patch(
        "src.api.questions.get_question_with_answers",
        new=AsyncMock(return_value=mock_question_read),
    ):
        response = await test_client.get("/questions/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["text"] == "Test question"


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
