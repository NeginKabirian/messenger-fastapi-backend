from typing import List
from models.User import User
from models.Message import Message
from pydantic import BaseModel


class Storage(BaseModel):
    users: List[User] = []
    messages = list[Message] = []
