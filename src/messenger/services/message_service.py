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
import messenger.models.User as User


logger = logging.getLogger(__name__)


async def send_message(
    messageDto: send_message_Dto, sender: User, db: AsyncSession
) -> bool:
    if not sender.is_logged_in:
        logger.error(f"Sender {sender.username} is marked as logged out!")
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


async def update_message(
    message_id: str, new_content: str, user: User, db: AsyncSession
) -> tuple[bool, str]:
    if not user.is_logged_in:
        logger.error(f"Sender {user.username} is marked as logged out!")
        return False
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    message = result.scalar_one_or_none()
    if not message:
        return False, "message_not_found"

    if message.sender_id != user.id:
        logger.warning(f"User {user.username} tried to edit a message they don't own.")
        return False, "forbidden"

    message.content = new_content

    await db.commit()
    logger.info(f"Message {message_id} was edited by {user.username}.")
    return True, "success"


async def get_inbox(user: User, db: AsyncSession) -> tuple[bool, str, List[Message]]:
    if user.is_logged_in:
        logger.info(f"'{user.username}' viewed their inbox.")
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
                selectinload(Message.recipients).selectinload(MessageRecipient.receiver),
            )
            .where(Message.id.in_(messages_id))
        )
        result2 = await db.execute(stmt2)
        messages_r = list(result2.scalars().all())

        stmt = (
            select(Message)
            .options(
                selectinload(Message.sender),
                selectinload(Message.recipients).selectinload(MessageRecipient.receiver),
            )
            .where(Message.sender_id == user.id)
        )
        result = await db.execute(stmt)
        messages_s = list(result.scalars().all())

        messages = messages_r + messages_s
        messages.sort(key=lambda x: x.created_at, reverse=True)
        return True, "", messages
    error = "unauthorized"
    logger.info(f"'{user.username}' must be logged in.")
    return False, error, []


async def get_messages(db: AsyncSession) -> list:
    logger.info(f"Get messages.")
    stmt = select(Message)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_message(message_id: str, user: User, db: AsyncSession) -> tuple[bool, str]:
    logger.debug(f"Attempting to delete message")
    if user.is_logged_in is False:
        error = "unauthorized"
        logger.info(f"'{user.username}' must be logged in.")
        return False, error
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    message = result.scalars().first()
    if not message:
        return False, "message_not_found"
    if message.sender_id != user.id:
        logger.warning(f"User {user.username} tried to edit a message they don't own.")
        return False, "forbidden"

    await db.delete(message)
    await db.commit()
    logger.info(f"Message deleted by {user.username} .")
    return True, "success"
