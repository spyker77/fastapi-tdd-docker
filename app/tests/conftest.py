from contextlib import asynccontextmanager

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings
from app.database import get_db
from app.main import create_application
from app.models import Base

TEST_USER = {
    "username": "test_user",
    "email": "test_user@mail.com",
    "full_name": "Test User",
    "password": "secret",
}

settings = get_settings()


def get_settings_override() -> Settings:
    return Settings(TESTING=1, DATABASE_URL=settings.DATABASE_TEST_URL)


app = create_application(api_versions=["v2"])
app.dependency_overrides[get_settings] = get_settings_override


async_engine = create_async_engine(settings.DATABASE_TEST_URL, connect_args={"check_same_thread": False})
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


@asynccontextmanager
async def setup_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        await async_engine.dispose()


@pytest.fixture
@asynccontextmanager
async def session() -> AsyncSession:
    async with setup_database():
        db = async_session()
        try:
            yield db
        finally:
            await db.close()


@pytest.fixture
@asynccontextmanager
async def test_client_with_db() -> AsyncClient:
    async with setup_database():

        async def override_get_db() -> AsyncSession:
            db = async_session()
            try:
                yield db
            finally:
                await db.close()

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(app=app, base_url="http://localhost:8000") as test_client:
            yield test_client
