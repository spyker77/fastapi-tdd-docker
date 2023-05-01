import pytest

from app.main import app


@pytest.mark.asyncio
async def test_home_page_message(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.get(url=app.url_path_for("home_page_message"))
        assert response.json()["message"] == "Please refer to the /docs or /redoc path to access the API documentation"
