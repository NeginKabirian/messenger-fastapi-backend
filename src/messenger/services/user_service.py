import logging
from messenger.models.User import User
from passlib.context import CryptContext
from messenger.schemas.user_schema import UserDto
import messenger.core.security as security
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from fastapi.security import OAuth2PasswordBearer
from messenger.core.database import get_db
from messenger.core.config import settings
from fastapi import Depends, HTTPException, status

oauth2_sheme = OAuth2PasswordBearer(tokenUrl="/users/login")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
logger = logging.getLogger(__name__)


async def get_current_user(
    token: str = Depends(oauth2_sheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="UNAUTHORIZED",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJTError:
        raise credentials_exception
    user = await get_user(username, db)
    if user is None:
        raise credentials_exception
    if not user.is_logged_in:
        raise HTTPException(status_code=401, detail="User logged out manually.")
    return user


async def sign_up(user: UserDto, db: AsyncSession) -> bool:
    logger.debug(f"Attempting to sign up user: {user.username}")
    stmt = select(User).where(User.username == user.username)
    result = await db.execute(stmt)
    exist = result.scalars().first()
    if exist:
        logger.error(f"Sign up failed. Username '{user.username}' already exists.")
        return False

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        phone=user.phone,
        name=user.name,
        bio=user.bio,
        birth_date=user.birth_date,
        gender=user.gender,
    )
    db.add(new_user)
    await db.commit()
    logger.info(f"User '{new_user.username}' successfully signed up.")
    return True


async def login(username: str, password: str, db: AsyncSession) -> User | None:
    logger.debug(f"Attempting to log in user: {username}")
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        logger.debug(f"verify_password for user {user.username}")
        if security.verify_password(password, user.hashed_password):
            user.is_logged_in = True
            await db.commit()
            logger.info(f"User '{user.username}' successfully logged in.")
            return user
    return None


async def update_user(user: User, user_dto: UserDto, db: AsyncSession) -> bool:
    logger.debug(f"Attempting to update user: {user.username}")
    stmt = select(User).where(User.username == user.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        user.hashed_password = pwd_context.hash(user_dto.password)
        user.username = user_dto.username
        user.email = user_dto.email
        user.phone = user_dto.phone
        user.name = user_dto.name
        user.bio = user_dto.bio
        user.birth_date = user_dto.birth_date
        user.gender = user_dto.gender
        await db.commit()
        logger.info(f"user: {user.username} updated.")
        return True
    logger.debug(f"user: {user.username} does not exist.")
    return False


async def get_users(db: AsyncSession) -> list:
    logger.info(f"Get users.")
    stmt = select(User)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_user(user: User, db: AsyncSession) -> bool:
    logger.debug(f"Attempting to delete user: {user.username}")
    stmt = select(User).where(User.username == user.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        await db.delete(user)
        await db.commit()
        logger.info(f"Messege:{user.username} deleted by .")
        return True
    logger.debug(f"user: {user.username} does not exist.")
    return False


async def logout_user(username: str, db: AsyncSession) -> bool:
    logger.debug(f"Attempting to logout user: {username}")
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        if user.is_logged_in is True:
            user.is_logged_in = False
            await db.commit()
            logger.info(f"user: {username} logged out.")
            return True
        else:
            logger.info(f"user: {username} is already logged out.")
            return False
    logger.debug(f"user: {username} does not exist.")
    return False


async def get_user(username: str, db: AsyncSession) -> User | None:
    logger.debug(f"Attempting to get user: {username}")
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        logger.info(f"user: {username} get.")
        return user
    return None
