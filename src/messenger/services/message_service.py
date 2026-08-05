from typing import List
import logging

from messenger.models.Message import Message
from messenger.models.storage import Storage
from messenger.models.User import User

logger = logging.getLogger(__name__)


def send_message(message: Message):
    Storage.messages.append(message)
    # log
    logger.info(f"New message sent by '{message.sender.username}'.")


def get_messages(user: User) -> list[Message]:
    logger.info(f"'{user.username}' viewed their inbox.")
    return [
        msg
        for msg in Storage.messages
        if msg.sender.username == user.username
        or any(r.username == user.username for r in msg.receiver)
    ]
