from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import get_settings
from app.schemas.token import TokenSchema
from app.security.auth import ACCESS_TOKEN_EXPIRE_DAYS, authenticate_user, create_access_token

settings = get_settings()
router = APIRouter(prefix=settings.AUTH_TOKEN_URL, tags=["token"])


@router.post("/", response_model=TokenSchema, description=f"⚠️ Token is valid for {ACCESS_TOKEN_EXPIRE_DAYS} days.")
async def issue_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
