from fastapi import APIRouter, HTTPException
import logging
import messenger.services.message_service as message_service
from messenger.schemas.send_message_shema import send_message_Dto

logger = logging.getLogger(__name__)
message_router = APIRouter(prefix="/messages", tags=["Messages"])


@message_router.post("", status_code=201)
def send_message(message: send_message_Dto):

    status = message_service.send_message(messageDto=message)
    if status:
        logger.info(f"New message sent by '{message.sender_username}'.")
        return {
            "status": "success",
            "message": f"New message sent by {message.sender_username} succussfully.",
        }
    logging.info(f"user {message.sender_username} must be logged in!")
    raise HTTPException(
        status_code=404, detail=f"user {message.sender_username} must be logged in!"
    )


@message_router.get("/{username}/inbox", status_code=200)
def get_inbox(username: str):
    status, error_type, messages = message_service.get_messages(username=username)
    if status:
        logger.info(f"'{username}' viewed their inbox via API.")
        if not messages:
            return {"status": "success", "data": [], "message": "Your inbox is empty."}
        resps = [
            f"From: {msg.sender} | Text: {msg.content} | Time: {msg.created_at.strftime('%H:%M')}"
            for msg in messages
        ]
        return {"status": "success", "data": resps}
    if error_type == "not_found":
        raise HTTPException(status_code=404, detail="User not found")
    elif error_type == "unauthorized":
        raise HTTPException(status_code=401, detail="User must be logged in")
