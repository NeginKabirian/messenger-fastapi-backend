from models.Message import Message
from models.storage import Storage
from models.User import User
from typing import List


def send_message(message: Message):
    Storage.messages.append(message)
    # log


def get_messages(user: User) -> List[Message]:
    messages = [
        msg
        for msg in Storage.messages
        if msg.sender.id == user.id or any(r.id == user.id for r in msg.receiver)
    ]
    # log
    return messages
