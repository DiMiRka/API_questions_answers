import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_create_answer(test_client: AsyncClient, mock_question_read, mock_answer_read):
    with patch(
        "src.api.answers.get_question_with_answers",
        new=AsyncMock(return_value=mock_question_read),
    ):
        with patch(
            "src.api.answers.create_answer", new=AsyncMock(return_value=mock_answer_read)
        ):
            response = await test_client.post(
                "/answers/question/1", json={"user_id": "user_1", "text": "Тест"}
            )

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Test answer"
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
async def test_get_answer_by_id(test_client: AsyncClient, mock_answer_read):
    with patch("src.api.answers.get_answer", new=AsyncMock(return_value=mock_answer_read)):
        response = await test_client.get("/answers/1")

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Test answer"
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
