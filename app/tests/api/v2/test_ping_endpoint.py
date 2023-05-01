import pytest

from app.main import app


@pytest.mark.asyncio
async def test_ping(test_client_with_db):
    async with test_client_with_db as client:
        response = await client.get(app.url_path_for("pong"))
        assert response.status_code == 200
        assert response.json() == {"ping": "pong!", "testing": True, "environment": "dev"}
