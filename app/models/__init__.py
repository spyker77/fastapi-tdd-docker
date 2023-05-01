from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy_utils import UUIDType


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AbstractBaseModel(TimestampMixin, Base):
    __abstract__ = True

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4, unique=True, nullable=False, index=True)


class Summary(AbstractBaseModel):
    __tablename__ = "summaries"

    url = Column(String)
    summary = Column(String)
    user_id = Column(UUIDType(binary=False), ForeignKey("users.id"))

    user = relationship("User", back_populates="summaries")

    def __str__(self):
        return self.url


class User(AbstractBaseModel):
    __tablename__ = "users"

    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    hashed_password = Column(String)

    summaries = relationship("Summary", back_populates="user")

    def __str__(self):
        return self.username
