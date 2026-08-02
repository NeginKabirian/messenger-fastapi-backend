from messenger.models.storage import Storage
import messenger.services.message_service as message_service
import messenger.services.user_service as user_service
import socket
import json
from messenger.core.logger import setup_logging
import logging
from messenger.models.User import User
from messenger.models.Message import Message

HOST = "127.0.0.1"
PORT = 65435

setup_logging()
logger = logging.getLogger(__name__)


def server_procces():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        logger.info("Socket successfully created")
        s.bind((HOST, PORT))
        s.listen()
        logger.info(f"Server is listening on {HOST}:{PORT}...")

        conn, addr = s.accept()
        while True:
            with conn:
                logger.info(f"Connected by {addr}")
                while True:
                    # User and opperand recv
                    data = conn.recv(4096)  # bythe
                    if not data:
                        break
                    text = data.decode("utf_8")
                    logger.debug(f"Received raw data{text}")

                    try:
                        req = json.loads(text)
                        command = req.get("command")
                        info = req.get("info")

                        if command == "SIGN_UP":
                            user = User(
                                **info
                            )  # convert dictionary(**kwargs) to user object with pydantic
                            check = user_service.sign_up(user)
                            if check:
                                resp = {
                                    "status": "success",
                                    "message": f"User: {user.username} signed up.",
                                }
                            else:
                                resp = {
                                    "status": "error",
                                    "message": f"User: {user.username} already exists.",
                                }
                            conn.sendall(json.dumps(resp).encode("utf_8"))
                        elif command == "LOG_IN":
                            username = info.get("username")
                            password = info.get("password")
                            logged_in_user = user_service.login(username, password)
                            if logged_in_user:
                                resp = {
                                    "status": "success",
                                    "message": f"User: {username} logged in.",
                                }
                            else:
                                resp = {
                                    "status": "error",
                                    "message": "Invalid username or password.",
                                }
                            conn.sendall(json.dumps(resp).encode("utf_8"))
                        elif command == "SEND_MSG":
                            curr_username = info.get("curr_username")
                            receiver_usernames = info.get("recv_usernames")
                            content = info.get("content")
                            curr_user = None
                            for u in Storage.users:
                                if u.username == curr_username:
                                    curr_user = u
                                    break
                            receiver_users = []
                            for u in Storage.users:
                                if u.username in receiver_usernames:
                                    receiver_users.append(u)

                            if curr_user is None or len(receiver_users) == 0:
                                resp = {
                                    "status": "error",
                                    "message": "Sender or Receiver not found!",
                                }
                            elif curr_user.is_logged_in == False:
                                resp = {
                                    "status": "error",
                                    "message": "You must log in first",
                                }
                            else:
                                message = Message(
                                    sender=curr_user,
                                    receiver=receiver_users,
                                    content=content,
                                )
                                message_service.send_message(message=message)
                                resp = {
                                    "status": "success",
                                    "message": "Message sent successfully!",
                                }
                            conn.sendall(json.dumps(resp).encode("utf_8"))
                        elif command == "INBOX":
                            curr_username = info.get("username")
                            curr_user = None
                            for u in Storage.users:
                                if u.username == curr_username:
                                    curr_user = u
                                    break
                            if curr_user is None:
                                resp = {"status": "error", "message": "User not found!"}
                                conn.sendall(json.dumps(resp).encode("utf_8"))
                                continue

                            messages = message_service.get_messages(curr_user)
                            if not messages:
                                resp = {
                                    "status": "success",
                                    "data": [],
                                    "message": "Your inbox is empty.",
                                }
                                conn.sendall(json.dumps(resp).encode("utf_8"))
                            else:
                                resps = []
                                for msg in messages:
                                    resps.append(
                                        f"From: {msg.sender.username} | Text: {msg.content} | Time: {msg.created_at.strftime('%H:%M')}"
                                    )
                                resp = {
                                    "status": "success",
                                    "data": resps,
                                    "message": f"{curr_user.username} viewed their inbox",
                                }
                                conn.sendall(json.dumps(resp).encode("utf_8"))
                        else:
                            error_res = {
                                "status": "error",
                                "message": "Unknown command",
                            }
                            conn.sendall(json.dumps(error_res).encode("utf-8"))
                    except Exception as e:
                        logger.error(f"Error processing request: {e}")
                        error_res = {
                            "status": "error",
                            "message": "Invalid request format",
                        }
                        conn.sendall(json.dumps(error_res).encode("utf-8"))


if __name__ == "__main__":
    server_procces()
