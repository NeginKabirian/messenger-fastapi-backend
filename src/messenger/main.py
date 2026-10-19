from fastapi import FastAPI

from messenger.core.logger import setup_logging
import logging
from messenger.routers.user_router import user_router
from messenger.routers.message_router import message_router
from messenger.routers.group_router import router

# http://127.0.0.1:8000/docs
setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="Messenger API")

app.include_router(user_router)
app.include_router(message_router)
app.include_router(router)


@app.get("/", status_code=200, tags=["General"])
def Welcome():

    return {"status": "success", "message": "Welcome to Messenger System"}


def start_api():
    import uvicorn

    uvicorn.run("messenger.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    start_api()
