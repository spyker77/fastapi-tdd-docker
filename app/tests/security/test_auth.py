import pytest

from app.config import get_settings
from app.models import User
from app.security.auth import create_access_token, get_current_active_user, get_current_user, get_password_hash

settings = get_settings()

CREDENTIALS_EXCEPTION = "HTTPException(status_code=401, detail='Could not validate credentials')"


@pytest.mark.asyncio
async def test_get_current_user_missing_username():
    jwt_without_username = create_access_token(data={})
    with pytest.raises(Exception) as e:
        assert await get_current_user(jwt_without_username)
    assert CREDENTIALS_EXCEPTION in str(e)


@pytest.mark.asyncio
async def test_get_current_user_fake_token():
    fake_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ8.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJleHAiOjE2Mjg5NjUzNjF8."
        "ZTEduygT8r7pxds4Dwg4CE185QNP8tlmQf8k850SS2o"
    )
    with pytest.raises(Exception) as e:
        assert await get_current_user(fake_token)
    assert CREDENTIALS_EXCEPTION in str(e)


@pytest.mark.asyncio
async def test_get_current_user_if_not_user(session):
    jwt_with_fake_username = create_access_token(data={"sub": "fake_username"})
    async with session as db:
        with pytest.raises(Exception) as e:
            assert await get_current_user(jwt_with_fake_username, db)
        assert CREDENTIALS_EXCEPTION in str(e)


@pytest.mark.asyncio
async def test_get_current_active_user_is_inactive(session):
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
        is_active=False,
    )

    async with session as db:
        async with db.begin():
            db.add(user)
            await db.commit()

            user_in_db = await db.get(User, user.id)
            with pytest.raises(Exception) as e:
                assert await get_current_active_user(user_in_db)
            assert "HTTPException(status_code=400, detail='Inactive user')" in str(e)
