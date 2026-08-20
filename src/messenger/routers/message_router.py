from fastapi import APIRouter, HTTPException, Depends
import logging
import messenger.services.message_service as message_service
from messenger.schemas.send_message_shema import send_message_Dto
from sqlalchemy.ext.asyncio import AsyncSession
from messenger.core.database import get_db
from messenger.schemas.EditMessageDto import EditMessageDto
from messenger.models.User import User
import messenger.services.user_service as user_service

logger = logging.getLogger(__name__)
message_router = APIRouter(prefix="/messages", tags=["Messages"])


@message_router.post("", status_code=201)
async def send_message(
    message: send_message_Dto,
    current_user: User = Depends(user_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):

    status = await message_service.send_message(
        messageDto=message, sender=current_user, db=db
    )
    if status:
        logger.info(f"New message sent by '{current_user.username}'.")
        return {
            "status": "success",
            "message": f"New message sent by {current_user.username} succussfully.",
        }
    logging.info(f"user {current_user.username} must be logged in!")
    raise HTTPException(
        status_code=401, detail=f"user {current_user.username} must be logged in!"
    )


@message_router.put("/{message_id}", status_code=200)
async def edit_message(
    message_id: str,
    data: EditMessageDto,
    current_user: User = Depends(user_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success, msg = await message_service.update_message(
        message_id, data.content, current_user, db
    )
    if not success:
        if msg == "unauthorized":
            raise HTTPException(status_code=401, detail=msg)
        elif msg == "message_not_found":
            raise HTTPException(status_code=404, detail=msg)
        elif msg == "forbidden":
            raise HTTPException(status_code=403, detail=msg)

    return {"status": "success", "message": "Succussfuly edit."}


@message_router.get("/inbox", status_code=200)
async def get_inbox(
    current_user: User = Depends(user_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status, error_type, messages = await message_service.get_inbox(
        user=current_user, db=db
    )
    if status:
        logger.info(f"'{current_user.username}' viewed their inbox via API.")
        if not messages:
            return {"status": "success", "data": [], "message": "Your inbox is empty."}

        resps = []
        for msg in messages:
            time_str = msg.created_at.strftime("%H:%M")

            if msg.sender.username == current_user.username:
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


@message_router.get("")
async def get_messages(db: AsyncSession = Depends(get_db)):
    logger.info("Get messages via API.")
    return await message_service.get_messages(db=db)


@message_router.delete("/{message_id}", status_code=200)
async def delete_message(
    message_id: str,
    current_user: User = Depends(user_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success, msg = await message_service.delete_message(message_id, current_user, db)
    if not success:
        if msg == "unauthorized":
            raise HTTPException(status_code=401, detail=msg)
        elif msg == "message_not_found":
            raise HTTPException(status_code=404, detail=msg)
        elif msg == "forbidden":
            raise HTTPException(status_code=403, detail=msg)

    return {"status": "success", "message": "Succussfuly delet."}
