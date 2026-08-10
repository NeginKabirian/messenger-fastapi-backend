import logging
from messenger.models.User import User
from messenger.models.storage import Storage
from passlib.context import CryptContext
from messenger.schemas.user_schema import UserDto
import messenger.core.security as security

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
logger = logging.getLogger(__name__)


def sign_up(user: UserDto) -> bool:
    logger.debug(f"Attempting to sign up user: {user.username}")
    for u in Storage.users:
        if u.username == user.username:
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
        gender=user.gender
    )
    Storage.users.append(new_user)
    logger.info(f"User '{new_user.username}' successfully signed up.")
    return True


def login(username: str, password: str) -> User | None:
    logger.debug(f"Attempting to log in user: {username}")

    for user in Storage.users:
        logger.debug(f"verify_password for user {user.username}{username}")
        if user.username == username:
            # hash function will be add later
            logger.debug(f"verify_password for user {user.username}")
            if security.verify_password(password, user.hashed_password):
                user.is_logged_in = True
                logger.info(f"User '{user.username}' successfully logged in.")
                return user

    return None


def update_user(username: str, user: UserDto) -> bool:
    logger.debug(f"Attempting to update user: {username}")
    for index, u in enumerate(Storage.users):
        if u.username == user.username:
            hashed_password = pwd_context.hash(user.password)
            updated_user = User(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password,
                phone=user.phone,
                name=user.name,
                bio=user.bio,
                birth_date=user.birth_date,
                gender=user.gender
            )
            Storage.users[index] = updated_user
            logger.info(f"user: {username} updated.")
            return True
    logger.debug(f"user: {username} does not exist.")
    return False


def get_users() -> list:
    logger.info(f"Get users.")
    return Storage.users


def delete_user(username: str) -> bool:
    logger.debug(f"Attempting to delete user: {username}")
    for index, u in enumerate(Storage.users):
        if u.username == username:
            Storage.users.pop(index)
            logger.info(f"user: {username} deleted.")
            return True
    logger.debug(f"user: {username} does not exist.")
    return False
