from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.crud import crud_user
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
async def create_user(payload: UserCreatePayloadSchema):
    return await crud_user.post(payload)


@router.get("/me/", response_model=UserSchema)
async def read_me(current_user: UserInDBSchema = Depends(get_current_active_user)):
    return current_user


@router.get("/me/summaries/", response_model=SummarySchemaList)
async def read_my_summaries(current_user: UserInDBSchema = Depends(get_current_active_user)):
    summaries = await crud_user.get_my_summaries(current_user.id)
    if not summaries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summaries not found")
    return summaries


@router.get("/{id}", response_model=UserSchema)
async def read_user(id: UUID = Path(...)):
    user = await crud_user.get(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/", response_model=UserSchemaList)
async def read_all_users():
    return await crud_user.get_all()


@router.put("/{id}", response_model=UserSchema)
async def update_user(
    payload: UserUpdatePayloadSchema,
    id: UUID = Path(...),
    current_user: UserInDBSchema = Depends(get_current_active_user),
):
    user = await crud_user.get(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if (id == current_user.id) or user["is_superuser"]:
        updated = await crud_user.put(id, payload)
        return updated
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient rights to update this user")


@router.delete("/{id}", response_model=UserSchema)
async def delete_user(id: UUID = Path(...), current_user: UserInDBSchema = Depends(get_current_active_user)):
    user = await crud_user.get(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if (id == current_user.id) or user["is_superuser"]:
        await crud_user.delete(id)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient rights to delete this user")
