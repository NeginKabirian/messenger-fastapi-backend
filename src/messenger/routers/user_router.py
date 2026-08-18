from fastapi import APIRouter, HTTPException, Depends
import logging
from messenger.schemas.user_schema import UserDto
from messenger.schemas.login_shema import LoginRequest
import messenger.services.user_service as user_service
from messenger.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("", status_code=201)
async def add_user(new_user: UserDto, db: AsyncSession = Depends(get_db)):
    status = await user_service.sign_up(user=new_user, db=db)
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


@user_router.put("/{username}", status_code=201)
async def update_user(username, new_user: UserDto, db: AsyncSession = Depends(get_db)):
    status = await user_service.update_user(username=username, user_dto=new_user, db=db)
    if status:
        logger.info(f"User {new_user.username} updated via API.")
        return {
            "status": "success",
            "message": f"user {new_user.username} updated succussfully.",
        }
    logger.error(f"Failed to update user{new_user.username}.user does not exist")
    raise HTTPException(status_code=400, detail="user does not exist")


@user_router.post("/login")
async def log_in(model: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.login(
        username=model.username, password=model.password, db=db
    )
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


@user_router.post("/{username}/logout")
async def logout(username: str, db: AsyncSession = Depends(get_db)):
    status = await user_service.logout_user(username=username, db=db)
    if status:
        return {
            "status": "success",
            "message": f"user {username} logged out succussfully.",
        }
    raise HTTPException(
        status_code=404, detail="username not found or is already logged out!"
    )


@user_router.get("")
async def get_users(db: AsyncSession = Depends(get_db)):
    logger.info("Get users via API.")
    return await user_service.get_users(db=db)


@user_router.get("/{username}")
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    logger.info("Get users via API.")
    user = await user_service.get_user(username=username, db=db)
    if user is None:
        raise HTTPException(
            status_code=404, detail="username not found or is already logged out!"
        )
    else:
        return {"status": "success", "data": user}


@user_router.delete("/{username}")
async def delete(username: str, db: AsyncSession = Depends(get_db)):
    status = await user_service.delete_user(username=username, db=db)
    if status:
        return {
            "status": "success",
            "message": f"user {username} deleted successfully.",
        }
    raise HTTPException(status_code=404, detail="username not found!")
