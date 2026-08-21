from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from messenger.core.database import Base
from uuid import uuid4
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .Message import Message
    from .MessageRecipient import MessageRecipient
    from .GroupMember import GroupMember


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: uuid4().hex, index=True
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gender: Mapped[str] = mapped_column(
        String, default="Prefer not to say", nullable=False
    )
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_logged_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    signup_ts: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    messages_sent: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_messages: Mapped[List["MessageRecipient"]] = relationship(
        "MessageRecipient", back_populates="receiver", cascade="all, delete-orphan"
    )
    group_memberships: Mapped[List["GroupMember"]] = relationship(
        "GroupMember", back_populates="user", cascade="all, delete-orphan"
    )
