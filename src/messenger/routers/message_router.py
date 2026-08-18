from fastapi import APIRouter, HTTPException, Depends
import logging
import messenger.services.message_service as message_service
from messenger.schemas.send_message_shema import send_message_Dto
from sqlalchemy.ext.asyncio import AsyncSession
from messenger.core.database import get_db

logger = logging.getLogger(__name__)
message_router = APIRouter(prefix="/messages", tags=["Messages"])


@message_router.post("", status_code=201)
async def send_message(message: send_message_Dto, db: AsyncSession = Depends(get_db)):

    status = await message_service.send_message(messageDto=message, db=db)
    if status:
        logger.info(f"New message sent by '{message.sender_username}'.")
        return {
            "status": "success",
            "message": f"New message sent by {message.sender_username} succussfully.",
        }
    logging.info(f"user {message.sender_username} must be logged in!")
    raise HTTPException(
        status_code=401, detail=f"user {message.sender_username} must be logged in!"
    )

@message_router.get("/{username}/inbox", status_code=200)
async def get_inbox(username: str, db: AsyncSession = Depends(get_db)):
    status, error_type, messages = await message_service.get_messages(
        username=username, db=db
    )
    if status:
        logger.info(f"'{username}' viewed their inbox via API.")
        if not messages:
            return {"status": "success", "data": [], "message": "Your inbox is empty."}

        resps = []
        for msg in messages:
            time_str = msg.created_at.strftime("%H:%M")

            if msg.sender.username == username:
                receivers_names = ", ".join(
                    [r.receiver.username for r in msg.recipients]
                )
                resps.append(
                    f"To: [{receivers_names}] | Text: {msg.content} | Time: {time_str}"
                )
            else:
                resps.append(
                    f"From: {msg.sender.username} | Text: {msg.content} | Time: {time_str}"
                )

        return {"status": "success", "data": resps}

    if error_type == "not_found":
        raise HTTPException(status_code=404, detail="User not found")
    elif error_type == "unauthorized":
        raise HTTPException(status_code=401, detail="User must be logged in")
