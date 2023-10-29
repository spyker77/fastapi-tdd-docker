from typing import List, Optional, TypeAlias

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


UserSchemaList: TypeAlias = List[UserSchema]


class UserInDBSchema(UserSchema):
    is_active: bool
    is_superuser: bool
    hashed_password: str

    class Config:
        from_attributes = True


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
