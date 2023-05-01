from typing import List
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy_utils import UUIDType


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class AbstractBaseModel(TimestampMixin, Base):
    __abstract__ = True

    id: Mapped[UUIDType] = mapped_column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        index=True,
    )


class Summary(AbstractBaseModel):
    __tablename__ = "summaries"

    url: Mapped[String] = mapped_column(String, index=True)
    summary: Mapped[String] = mapped_column(String)
    user_id: Mapped[UUIDType] = mapped_column(UUIDType(binary=False), ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates="summaries")

    def __str__(self):
        return self.url


class User(AbstractBaseModel):
    __tablename__ = "users"

    username: Mapped[String] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[String] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[String] = mapped_column(String)
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[Boolean] = mapped_column(Boolean, default=False)
    hashed_password: Mapped[String] = mapped_column(String)

    summaries: Mapped[List["Summary"]] = relationship("Summary", back_populates="user")

    def __str__(self):
        return self.username
