import pytest

from app.main import app


@pytest.mark.asyncio
async def test_access_token_with_invalid_data(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.post(
            url=app.url_path_for("issue_access_token"),
            data={"username": "not_exist", "password": "none"},
        )
        assert response.json()["detail"] == "Incorrect username or password"
