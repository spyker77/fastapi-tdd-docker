import pytest

from app.config import get_settings
from app.models import Summary, User
from app.security.auth import get_password_hash

settings = get_settings()


@pytest.mark.asyncio
async def test_text_summary_str_method(session):
    async with session as db:
        async with db.begin():
            payload = {
                "username": "test",
                "email": "test@mail.com",
                "full_name": "Test User",
                "password": "secret",
            }
            user = User(
                username=payload["username"],
                email=payload["email"],
                full_name=payload["full_name"],
                hashed_password=get_password_hash(payload["password"]),
            )
            db.add(user)
            await db.commit()

        async with db.begin():
            test_url = "https://lipsum.com/"
            summary = Summary(url=test_url, summary="", user_id=user.id)
            db.add(summary)
            await db.commit()
            assert str(summary.url) == test_url
