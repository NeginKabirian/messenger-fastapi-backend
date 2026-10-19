from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from messenger.core.database import Base
from datetime import datetime

if TYPE_CHECKING:
    from .User import User
    from .Message import Message


class MessageRecipient(Base):
    __tablename__ = "message_recipients"
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id"), primary_key=True)
    receiver_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    delivery_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    message: Mapped["Message"] = relationship("Message", back_populates="recipients")
    receiver: Mapped["User"] = relationship("User", back_populates="received_messages")
