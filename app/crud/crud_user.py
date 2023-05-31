from typing import Dict, List, Optional

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Summary, User
from app.schemas.user import UserCreatePayloadSchema, UserUpdatePayloadSchema
from app.security.auth import get_password_hash


async def post(payload: UserCreatePayloadSchema, db: AsyncSession = Depends(get_db)) -> User:
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get(user_id: int, db: AsyncSession = Depends(get_db)) -> Optional[Dict]:
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if user:
        return user
    return None


async def get_all(db: AsyncSession = Depends(get_db)) -> List[Dict]:
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [user for user in users]


async def get_my_summaries(user_id: int, db: AsyncSession = Depends(get_db)) -> Optional[List[Dict]]:
    result = await db.execute(select(Summary).filter_by(user_id=user_id))
    summaries = result.scalars().all()
    if summaries:
        return [summary for summary in summaries]
    return None


async def put(user_id: int, payload: UserUpdatePayloadSchema, db: AsyncSession = Depends(get_db)) -> Dict:
    new_data = payload.dict(exclude_unset=True, exclude_defaults=True, exclude_none=True)
    if "password" in new_data:
        new_data["hashed_password"] = get_password_hash(new_data["password"])
        del new_data["password"]

    await db.execute(update(User).where(User.id == user_id).values(**new_data))
    await db.commit()

    result = await db.execute(select(User).filter_by(id=user_id))
    updated_user = result.scalars().first()

    return updated_user


async def remove(user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
