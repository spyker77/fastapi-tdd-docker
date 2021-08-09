from typing import Iterator, NewType

import pytest
from fastapi.testclient import TestClient
from requests.models import Response
from tortoise.contrib.fastapi import register_tortoise

from app.config import Settings, get_settings
from app.main import create_application

TEST_USER = {
    "username": "test_user",
    "email": "test_user@mail.com",
    "full_name": "Test User",
    "password": "secret",
}

JWT = NewType("JWT", str)

settings = get_settings()


def get_settings_override() -> Settings:
    return Settings(TESTING=1, DATABASE_URL=settings.DATABASE_TEST_URL)


app = create_application(api_versions=["v2"])
app.dependency_overrides[get_settings] = get_settings_override


@pytest.fixture(scope="function")
def test_client_with_db() -> Iterator[TestClient]:
    register_tortoise(
        app,
        db_url=get_settings_override().DATABASE_URL,
        modules={"models": settings.MODELS},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def create_test_user(test_client_with_db: TestClient) -> Response:
    response = test_client_with_db.post(url=app.url_path_for("create_user"), json=TEST_USER)
    return response


@pytest.fixture(scope="function")
def issued_test_token(test_client_with_db: TestClient) -> JWT:
    response = test_client_with_db.post(
        url=app.url_path_for("issue_access_token"),
        data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
    )
    tokens = response.json()
    return tokens["access_token"]


@pytest.fixture(scope="function")
def create_test_summary(test_client_with_db: TestClient, issued_test_token: str) -> Response:
    response = test_client_with_db.post(
        url=app.url_path_for("create_summary"),
        json={"url": "https://lipsum.com/"},
        headers={"Authorization": f"Bearer {issued_test_token}"},
    )
    return response
