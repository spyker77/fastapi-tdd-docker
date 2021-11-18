from typing import Dict, List, Optional
from uuid import UUID

from app.models import Summary, User
from app.schemas.user import UserCreatePayloadSchema, UserUpdatePayloadSchema
from app.security.auth import create_password_hash


async def post(payload: UserCreatePayloadSchema) -> User:
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=create_password_hash(payload.password),
    )
    await user.save()
    return user


async def get(id: UUID) -> Optional[Dict]:
    if user := await User.filter(id=id).first():
        return dict(user)
    return None


async def get_all() -> List[Dict]:
    return await User.all().values()


async def get_my_summaries(user_id: UUID) -> Optional[List[Dict]]:
    if summaries := await Summary.filter(user_id=user_id).values():
        return summaries
    return None


async def put(id: UUID, payload: UserUpdatePayloadSchema) -> Dict:
    new_data = payload.dict(exclude_unset=True, exclude_defaults=True, exclude_none=True)
    if "password" in new_data:
        new_data["hashed_password"] = create_password_hash(new_data["password"])
        del new_data["password"]
    await User.filter(id=id).update(**new_data)
    updated_user = await User.filter(id=id).first()
    return dict(updated_user)  # type: ignore


async def delete(id: UUID) -> None:
    await User.filter(id=id).delete()
