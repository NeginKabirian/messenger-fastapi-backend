from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field


MessageType = Literal["text", "image", "voice"]


class Message(BaseModel):
    sender: str
    receiver: List[str]
    message_type: MessageType = "text"
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    delivery_time: datetime | None = None
    is_read: bool = False
