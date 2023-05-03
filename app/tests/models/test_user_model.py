import pytest

from app.config import get_settings
from app.models import User
from app.security.auth import get_password_hash

settings = get_settings()


@pytest.mark.asyncio
async def test_user_str_representation(session):
    async with session as db:
        async with db.begin():
            payload = {"username": "test", "email": "test@mail.com", "full_name": "Test User", "password": "secret"}
            user = User(
                username=payload["username"],
                email=payload["email"],
                full_name=payload["full_name"],
                hashed_password=get_password_hash(payload["password"]),
            )
            db.add(user)
            await db.commit()

        async with db.begin():
            user_in_db = await db.get(User, user.id)
            assert str(user_in_db) == payload["username"]
