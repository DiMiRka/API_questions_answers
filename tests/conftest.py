from unittest.mock import AsyncMock, MagicMock
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.core.db_config import get_async_session
from src.main import app


@pytest_asyncio.fixture
async def mock_session():
    from sqlalchemy.ext.asyncio import AsyncSession

    session = AsyncMock(spec=AsyncSession)

    # Базовая настройка мока
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()

    return session


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
