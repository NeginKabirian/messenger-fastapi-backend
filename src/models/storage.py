from typing import List
from models.User import User
from models.Message import Message


class Storage:
    users: List[User] = []
    messages: list[Message] = []
