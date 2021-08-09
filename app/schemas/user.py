from typing import List, Optional, Type
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str] = None


UserSchemaList: Type[List] = List[UserSchema]


class UserInDBSchema(UserSchema):
    is_active: bool
    is_superuser: bool
    hashed_password: str


class UserPayloadSchema(BaseModel):
    full_name: Optional[str] = None


class UserCreatePayloadSchema(UserPayloadSchema):
    username: str
    email: EmailStr
    password: str


class UserUpdatePayloadSchema(UserPayloadSchema):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
