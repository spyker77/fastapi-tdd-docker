import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.fastapi import register_tortoise

from app.config import MODELS, Settings, get_settings
from app.main import create_application


def get_settings_override():
    return Settings(testing=1, database_url=get_settings().database_test_url)


app = create_application(api_versions=["v2"])
app.dependency_overrides[get_settings] = get_settings_override


@pytest.fixture(scope="module")
def test_app():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def test_app_with_db():
    register_tortoise(
        app,
        db_url=get_settings().database_test_url,
        modules={"models": MODELS},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as test_client:
        yield test_client
