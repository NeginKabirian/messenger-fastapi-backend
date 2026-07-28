import logging
from messenger.models.User import User
from messenger.models.storage import Storage

logger = logging.getLogger(__name__)


def sign_up(new_user: User) -> bool:
    logger.debug(f"Attempting to sign up user: {new_user.username}")
    for user in Storage.users:
        # hash function will be add later
        if user.username == new_user.username:
            logger.error(
                f"Sign up failed. Username '{new_user.username}' already exists."
            )
            return False
    Storage.users.append(new_user)
    # log
    logger.info(f"User '{new_user.username}' successfully signed up.")
    return True


def login(username: str, password: str) -> User | None:
    logger.debug(f"Attempting to log in user: {username}")
    for user in Storage.users:
        if user.username == username:
            # hash function will be add later
            if user.hashed_password == password:
                user.is_logged_in = True
                logger.info(f"User '{user.username}' successfully logged in.")
                return user

    return None
