from unittest.mock import AsyncMock, Mock, MagicMock
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime

from src.core.db_config import get_async_session
from src.main import app
from src.models.questions_answers import Question, Answer
from src.schemas.questions_answers import QuestionRead, AnswerRead


# Моки для ORM моделей
@pytest.fixture
def mock_question_model():
    question = MagicMock(spec=Question)
    question.id = 1
    question.text = "Test question"
    question.answers = []
    return question


@pytest.fixture
def mock_answer_model():
    answer = MagicMock(spec=Answer)
    answer.id = 1
    answer.question_id = 1
    answer.user_id = "user_1"
    answer.text = "Test answer"
    return answer


# Моки для Pydantic схем
@pytest.fixture
def mock_question_read():
    return QuestionRead(id=1, text="Test question", created_at=datetime.now(), answers=[])


@pytest.fixture
def mock_answer_read():
    return AnswerRead(
        id=1, question_id=1, user_id="user_1", text="Test answer", created_at=datetime.now()
    )


# Моки для нескольких вопросов/ответов
@pytest.fixture
def mock_questions_list(mock_question_read):
    question2 = QuestionRead(
        id=2, text="Second question", created_at=datetime.now(), answers=[]
    )
    return [mock_question_read, question2]


@pytest.fixture
def mock_answers_list(mock_answer_read):
    answer2 = AnswerRead(
        id=2, question_id=1, user_id="user_2", text="Second answer", created_at=datetime.now()
    )
    return [mock_answer_read, answer2]


# Мок сессии БД
@pytest_asyncio.fixture
async def mock_session():
    from sqlalchemy.ext.asyncio import AsyncSession

    session = AsyncMock(spec=AsyncSession)

    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = Mock()  # Синхронный метод
    session.delete = AsyncMock()  # Синхронный метод
    session.refresh = AsyncMock()

    return session


# Тестовый клиент
@pytest_asyncio.fixture
async def test_client(mock_session):
    async def override_db():
        yield mock_session

    app.dependency_overrides[get_async_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


# Тестовые данные для запросов
@pytest.fixture
def create_question_payload():
    return {"text": "New question"}


@pytest.fixture
def create_answer_payload():
    return {"user_id": "user_1", "text": "New answer"}
