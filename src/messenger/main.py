from fastapi import FastAPI

from messenger.core.logger import setup_logging
import logging
from messenger.routers.user_router import router

# http://127.0.0.1:8000/docs
setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="Messenger API")

app.include_router(router)


@app.get("/", status_code=200, tags=["General"])
def Welcome():

    return {"status": "success", "message": "Welcome to Messenger System"}
