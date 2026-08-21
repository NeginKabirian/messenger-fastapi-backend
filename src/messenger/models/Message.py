from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from messenger.core.database import Base
from uuid import uuid4
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .User import User
    from .MessageRecipient import MessageRecipient
    from .Group import Group


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: uuid4().hex, index=True
    )
    sender_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    group_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=True
    )
    message_type: Mapped[str] = mapped_column(String, nullable=False, default="text")
    content: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    sender: Mapped["User"] = relationship(
        "User", foreign_keys=[sender_id], back_populates="messages_sent"
    )
    recipients: Mapped[List["MessageRecipient"]] = relationship(
        "MessageRecipient", back_populates="message", cascade="all, delete-orphan"
    )
    group: Mapped[Optional["Group"]] = relationship("Group", back_populates="messages")
