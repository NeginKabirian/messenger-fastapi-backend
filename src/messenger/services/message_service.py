from typing import List
import logging
from messenger.models.Message import Message
from messenger.models.MessageRecipient import MessageRecipient
from messenger.schemas.send_message_shema import send_message_Dto
from messenger.services.user_service import get_user
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


logger = logging.getLogger(__name__)


async def send_message(messageDto: send_message_Dto, db: AsyncSession) -> bool:
    sender = await get_user(messageDto.sender_username, db=db)
    if sender is None or not sender.is_logged_in:
        logger.error(f"Sender {messageDto.sender_username} not found or not logged in!")
        return False

    sender.last_seen = datetime.now()

    valid_receivers = []
    for username in messageDto.receiver_username:
        user = await get_user(username=username, db=db)
        if user is not None:
            valid_receivers.append(user)

    if len(valid_receivers) == 0:
        logger.error("No valid receivers found!")
        return False

    message = Message(sender_id=sender.id, content=messageDto.content)
    for r in valid_receivers:
        Recipient = MessageRecipient(receiver_id=r.id)
        message.recipients.append(Recipient)

    db.add(message)
    await db.commit()
    logger.info(f"New message sent by '{sender.username}'.")
    return True


async def get_messages(
    username: str, db: AsyncSession
) -> tuple[bool, str, List[Message]]:
    user = await get_user(username=username, db=db)
    if user is None:
        error = "not_found"
        logger.info(f"'{username}' does not exist.")
        return False, error, []
    if user.is_logged_in:
        logger.info(f"'{username}' viewed their inbox.")
        messages = []
        stmt1 = select(MessageRecipient.message_id).where(
            MessageRecipient.receiver_id == user.id
        )
        result1 = await db.execute(stmt1)
        messages_id = list(result1.scalars().all())

        stmt2 = (
            select(Message)
            .options(
                selectinload(Message.sender),
                selectinload(Message.recipients).selectinload(
                    MessageRecipient.receiver
                ),
            )
            .where(Message.id.in_(messages_id))
        )
        result2 = await db.execute(stmt2)
        messages_r = list(result2.scalars().all())

        stmt = (
            select(Message)
            .options(
                selectinload(Message.sender),
                selectinload(Message.recipients).selectinload(
                    MessageRecipient.receiver
                ),
            )
            .where(Message.sender_id == user.id)
        )
        result = await db.execute(stmt)
        messages_s = list(result.scalars().all())

        messages = messages_r + messages_s
        messages.sort(key=lambda x: x.created_at, reverse=True)
        return True, "", messages
    error = "unauthorized"
    logger.info(f"'{username}' must be logged in.")
    return False, error, []
