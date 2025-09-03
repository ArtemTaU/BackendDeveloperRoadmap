from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, UUID, String, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]


class BaseUser(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    email = Column(String(100), unique=True, index=True)
    email_is_verified = Column(Boolean, default=False)

    username = Column(String(100), index=True, nullable=True, unique=True)
    hashed_password = Column(String(100))

    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow())
