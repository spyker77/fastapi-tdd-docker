import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy_utils import UUIDType


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_at: Mapped[datetime.datetime] = mapped_column(
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

    url: Mapped[str] = mapped_column(index=True)
    summary: Mapped[str]
    user_id: Mapped[UUIDType] = mapped_column(UUIDType(binary=False), ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="summaries")

    def __str__(self):
        return self.url


class User(AbstractBaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    hashed_password: Mapped[str]

    summaries: Mapped[list["Summary"]] = relationship(back_populates="user")

    def __str__(self):
        return self.username
