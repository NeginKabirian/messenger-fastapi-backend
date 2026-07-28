from typing import List
from .User import User
from .Message import Message


class Storage:
    users: List[User] = []
    messages: list[Message] = []
