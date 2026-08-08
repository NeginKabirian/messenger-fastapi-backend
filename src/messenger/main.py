from fastapi import FastAPI, HTTPException
from messenger.models.User import User
import messenger.services.user_service as user_service
from messenger.core.logger import setup_logging
import logging

# http://127.0.0.1:8000/docs
setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="Messenger API")


@app.get("/", status_code=200)
def Wellcome():

    return {"status": "success", "message": "Welcome to Messenger System"}


# @app.post("/users")
