from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.models import User
from app.schemas.token import TokenDataSchema
from app.schemas.user import UserInDBSchema

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.AUTH_TOKEN_URL)


def create_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(username: Optional[str]):
    if user := await User.filter(username=username).first():
        return UserInDBSchema(**dict(user))


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if user and verify_password(password, user.hashed_password):
        return user
    return False


def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
        token_data = TokenDataSchema(username=username)
        user = await get_user(token_data.username)
        if not user:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
