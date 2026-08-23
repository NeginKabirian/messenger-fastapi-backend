from fastapi import APIRouter, HTTPException, Depends, status
import logging
from messenger.schemas.user_schema import UserDto
from messenger.schemas.login_shema import LoginRequest
import messenger.services.user_service as user_service
from messenger.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from messenger.core.security import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
import messenger.models.User as User

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


@user_router.put("", status_code=201)
async def update_user(
    new_user: UserDto,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    status = await user_service.update_user(
        user=current_user.username, user_dto=new_user, db=db
    )
    if status:
        logger.info(f"User {new_user.username} updated via API.")
        return {
            "status": "success",
            "message": f"user {new_user.username} updated succussfully.",
        }
    logger.error(f"Failed to update user{new_user.username}.user does not exist")
    raise HTTPException(status_code=400, detail="user does not exist")


@user_router.post("/log_in")
async def log_in(model: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.login(username=model.username, password=model.password, db=db)
    if user is not None:
        if user.is_logged_in:
            logger.info(f"User {user.username} logged in via API.")
            return {
                "status": "success",
                "message": f"user {user.username} logged in succussfully.",
            }
    else:
        logger.error(f"Failed to log in user {model.username}")
        raise HTTPException(status_code=404, detail="password or username was not correct")


@user_router.post("/login")
async def login(
    data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await user_service.get_user(data.username, db)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="password or username was not correct")
    user.is_logged_in = True
    await db.commit()
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("/logout")
async def logout(
    user: User = Depends(user_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status = await user_service.logout_user(user=user, db=db)
    if status:
        return {
            "status": "success",
            "message": f"user {user.username} logged out succussfully.",
        }
    raise HTTPException(
        status_code=404, detail="username not found or is already logged out!"
    )


@user_router.get("")
async def get_users(
    admin_user: User = Depends(user_service.get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Get users via API.")
    return await user_service.get_users(db=db)


@user_router.get("/{username}")
async def get_user(
    username: str,
    admin_user: User = Depends(user_service.get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Get users via API.")
    user = await user_service.get_user(username=username, db=db)
    if user is None:
        raise HTTPException(
            status_code=404, detail="username not found or is already logged out!"
        )
    else:
        return {"status": "success", "data": user}


@user_router.delete("")
async def delete(
    username: str,
    admin_user: User = Depends(user_service.get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    status = await user_service.delete_user(username=username, db=db)
    if status:
        return {
            "status": "success",
            "message": f"user {username} deleted successfully.",
        }
    raise HTTPException(status_code=404, detail="username not found!")
