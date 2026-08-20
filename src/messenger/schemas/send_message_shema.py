from pydantic import BaseModel, Field
from typing import List


class send_message_Dto(BaseModel):
    receiver_username: List[str]
    content: str
