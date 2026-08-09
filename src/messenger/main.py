from fastapi import FastAPI, HTTPException
from messenger.models.User import User
import messenger.services.user_service as user_service
from messenger.core.logger import setup_logging
import logging
from messenger.schemas.user_schema import UserDto
from messenger.schemas.login_shema import LoginRequest


# http://127.0.0.1:8000/docs
setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="Messenger API")


@app.get("/", status_code=200)
def Welcome():

    return {"status": "success", "message": "Welcome to Messenger System"}


@app.post("/user", status_code=201)
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


@app.put("/user/{username}", status_code=201)
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


@app.post("/user/login")
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
@app.get("/users")
def get_users():
    logger.info("Get users via API.")
    return user_service.get_users()

@app.delete("/user/{username}")
def delete(username: str):
    status = user_service.delete_user(username=username)
    if status:
        return {
                "status": "success",
                "message": f"user {username} deleted succussfully.",
            }
    raise HTTPException(
            status_code=404, detail="username not found!"
        )
 
