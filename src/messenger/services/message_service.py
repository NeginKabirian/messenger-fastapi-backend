from typing import List
import logging
from messenger.models.Message import Message
from messenger.models.storage import Storage
from messenger.models.User import User
from messenger.schemas.send_message_shema import send_message_Dto
from messenger.services.user_service import get_user
from datetime import datetime


logger = logging.getLogger(__name__)


def send_message(messageDto: send_message_Dto) -> bool:
    sender = get_user(messageDto.sender_username)
    if sender is None or not sender.is_logged_in:
        logger.error(f"Sender {messageDto.sender_username} not found or not logged in!")
        return False

    sender.last_seen = datetime.now()

    valid_receivers = []
    for username in messageDto.receiver_username:
        if get_user(username) is not None:
            valid_receivers.append(username)

    if len(valid_receivers) == 0:
        logger.error("No valid receivers found!")
        return False

    message = Message(
        sender=messageDto.sender_username,
        receiver=valid_receivers,
        content=messageDto.content,
    )

    Storage.messages.append(message)
    logger.info(f"New message sent by '{message.sender}'.")
    return True


def get_messages(username: str) -> tuple[bool, str, List[Message]]:
    user = get_user(username=username)
    if user is None:
        error = "not_found"
        logger.info(f"'{username}' does not exist.")
        return False, error, []
    if user.is_logged_in:
        logger.info(f"'{username}' viewed their inbox.")
        messages = []
        for msg in Storage.messages:
            if msg.sender == username or username in msg.receiver:
                messages.append(msg)

        return True, "", messages
    error = "unauthorized"
    logger.info(f"'{username}' must be logged in.")
    return False, error, []
