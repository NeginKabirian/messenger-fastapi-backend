from fastapi import FastAPI, HTTPException
from messenger.models.User import User
import messenger.services.user_service as user_service
from messenger.core.logger import setup_logging
import logging
from messenger.schemas.user_schema import UserDto
from passlib.context import CryptContext

# http://127.0.0.1:8000/docs
setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="Messenger API")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@app.get("/", status_code=200)
def Welcome():

    return {"status": "success", "message": "Welcome to Messenger System"}


@app.post("/user", status_code=201)
def add_user(new_user: UserDto):
    hashed_password = pwd_context.hash(new_user.password)
    user = User(
        username=new_user.username,
        email=new_user.email,
        hashed_password=hashed_password,
        phone=new_user.phone,
        name=new_user.name,
        bio=new_user.bio,
        birth_date=new_user.birth_date
    )
    status = user_service.sign_up(new_user=user)
    if status:
        logger.info(f"User {user.username} created via API.")
        return {
            "status": "success",
            "message": f"user{user.username} add succussfully.",
        }
    logger.error(f"Failed to create user{user.username}.")
    raise HTTPException(status_code=400)
