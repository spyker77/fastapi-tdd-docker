import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.fastapi import register_tortoise

from app.config import Settings, get_settings
from app.main import create_application

settings = get_settings()


def get_settings_override():
    return Settings(TESTING=1, DATABASE_URL=settings.DATABASE_TEST_URL)


app = create_application()
app.dependency_overrides[get_settings] = get_settings_override


@pytest.fixture(scope="function")
def test_app_with_db():
    register_tortoise(
        app,
        db_url=get_settings_override().DATABASE_URL,
        modules={"models": settings.MODELS},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as test_client:
        yield test_client
