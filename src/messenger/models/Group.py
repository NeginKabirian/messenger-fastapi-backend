from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from messenger.core.database import Base
from datetime import datetime
from uuid import uuid4
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .User import User
    from .Message import Message
    from .GroupMember import GroupMember


class Group(Base):
    __tablename__ = "groups"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: uuid4().hex, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id])
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="group", cascade="all, delete-orphan"
    )
    members: Mapped[List["GroupMember"]] = relationship(
        "GroupMember", back_populates="group", cascade="all, delete-orphan"
    )
