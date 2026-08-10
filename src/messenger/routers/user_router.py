# src/messenger/routers/user_router.py
from fastapi import APIRouter, HTTPException
import logging
from messenger.models.User import User
from messenger.schemas.user_schema import UserDto
from messenger.schemas.login_shema import LoginRequest
import messenger.services.user_service as user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=201)
def add_user(new_user: UserDto):
    status = user_service.sign_up(user=new_user)
    if status:
        logger.info(f"User {new_user.username} created via API.")
        return {
            "status": "success",
            "message": f"user {new_user.username} add succussfully.",
        }
    logger.error(f"Failed to create user{new_user.username}.")
    raise HTTPException(
        status_code=400, detail=f"Username {new_user.username} already exists."
    )


@router.put("/{username}", status_code=201)
def update_user(username, new_user: UserDto):
    status = user_service.update_user(username=username, user=new_user)
    if status:
        logger.info(f"User {new_user.username} updated via API.")
        return {
            "status": "success",
            "message": f"user {new_user.username} updated succussfully.",
        }
    logger.error(f"Failed to update user{new_user.username}.user does not exist")
    raise HTTPException(status_code=400, detail="user does not exist")


@router.post("/login")
def log_in(model: LoginRequest):
    user = user_service.login(username=model.username, password=model.password)
    if user is not None:
        if user.is_logged_in:
            logger.info(f"User {user.username} logged in via API.")
            return {
                "status": "success",
                "message": f"user {user.username} logged in succussfully.",
            }
    else:
        logger.error(f"Failed to log in user {model.username}")
        raise HTTPException(
            status_code=404, detail="password or username was not correct"
        )


@router.post("/{username}/logout")
def logout(username: str):
    status = user_service.logout_user(username=username)
    if status:
        return {
            "status": "success",
            "message": f"user {username} logged out succussfully.",
        }
    raise HTTPException(
        status_code=404, detail="username not found or is already logged out!"
    )


@router.get("")
def get_users():
    logger.info("Get users via API.")
    return user_service.get_users()


@router.delete("/{username}")
def delete(username: str):
    status = user_service.delete_user(username=username)
    if status:
        return {
            "status": "success",
            "message": f"user {username} deleted successfully.",
        }
    raise HTTPException(status_code=404, detail="username not found!")
