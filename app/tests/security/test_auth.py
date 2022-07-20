import pytest
from tortoise import Tortoise

from app.config import get_settings
from app.models import User
from app.security.auth import create_access_token, create_password_hash, get_current_active_user, get_current_user

settings = get_settings()


@pytest.mark.asyncio
async def test_get_current_user_missing_username():
    credentials_exception = "HTTPException(status_code=401, detail='Could not validate credentials')"
    jwt_without_username = create_access_token(data={})
    with pytest.raises(Exception) as e:
        assert await get_current_user(jwt_without_username)
    assert credentials_exception in str(e)


@pytest.mark.asyncio
async def test_get_current_user_fake_token():
    credentials_exception = "HTTPException(status_code=401, detail='Could not validate credentials')"
    fake_token = """eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ8.
    eyJzdWIiOiJ0ZXN0X3VzZXIiLCJleHAiOjE2Mjg5NjUzNjF8.
    ZTEduygT8r7pxds4Dwg4CE185QNP8tlmQf8k850SS2o
    """
    with pytest.raises(Exception) as e:
        assert await get_current_user(fake_token)
    assert credentials_exception in str(e)


@pytest.mark.asyncio
async def test_get_current_user_if_not_user():
    try:
        await Tortoise.init(db_url=settings.DATABASE_TEST_URL, modules={"models": settings.MODELS})
        await Tortoise.generate_schemas()
        credentials_exception = "HTTPException(status_code=401, detail='Could not validate credentials')"
        jwt_with_fake_username = create_access_token(data={"sub": "fake_username"})
        with pytest.raises(Exception) as e:
            assert await get_current_user(jwt_with_fake_username)
        assert credentials_exception in str(e)
    finally:
        await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_get_current_active_user_is_inactive():
    try:
        await Tortoise.init(db_url=settings.DATABASE_TEST_URL, modules={"models": settings.MODELS})
        await Tortoise.generate_schemas()
        payload = {"username": "test", "email": "test@mail.com", "full_name": "Test User", "password": "secret"}
        user = User(
            username=payload["username"],
            email=payload["email"],
            full_name=payload["full_name"],
            hashed_password=create_password_hash(payload["password"]),
            is_active=False,
        )
        await user.save()
        user_in_db = await User.filter(id=user.id).first()
        with pytest.raises(Exception) as e:
            assert await get_current_active_user(user_in_db)
        assert "HTTPException(status_code=400, detail='Inactive user')" in str(e)
    finally:
        await Tortoise.close_connections()
