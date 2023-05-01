from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_user
from app.database import get_db
from app.schemas.summary import SummarySchemaList
from app.schemas.user import (
    UserCreatePayloadSchema,
    UserInDBSchema,
    UserSchema,
    UserSchemaList,
    UserUpdatePayloadSchema,
)
from app.security.auth import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreatePayloadSchema, db: AsyncSession = Depends(get_db)):
    user = await crud_user.post(payload=payload, db=db)
    return user


@router.get("/me/", response_model=UserSchema)
async def read_me(current_user: UserInDBSchema = Depends(get_current_active_user)):
    return current_user


@router.get("/me/summaries/", response_model=SummarySchemaList)
async def read_my_summaries(
    current_user: UserInDBSchema = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    summaries = await crud_user.get_my_summaries(user_id=current_user.id, db=db)
    if not summaries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summaries not found")
    return summaries


@router.get("/{id}", response_model=UserSchema)
async def read_user(id: UUID = Path(...), db: AsyncSession = Depends(get_db)):
    user = await crud_user.get(user_id=id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/", response_model=UserSchemaList)
async def read_all_users(db: AsyncSession = Depends(get_db)):
    return await crud_user.get_all(db=db)


@router.put("/{id}", response_model=UserSchema)
async def update_user(
    payload: UserUpdatePayloadSchema,
    id: UUID = Path(...),
    current_user: UserInDBSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get(user_id=id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if (id == current_user.id) or user["is_superuser"]:
        updated = await crud_user.put(user_id=id, payload=payload, db=db)
        return updated
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient rights to update this user")


@router.delete("/{id}", response_model=UserSchema)
async def delete_user(
    id: UUID = Path(...),
    current_user: UserInDBSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get(user_id=id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if (id == current_user.id) or user["is_superuser"]:
        await crud_user.remove(user_id=id, db=db)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient rights to delete this user")
