from messenger.models.storage import Storage
import messenger.services.message_service as message_service
import messenger.services.user_service as user_service
import socket
import json
from messenger.core.logger import setup_logging
import logging
from messenger.models.User import User
from messenger.models.Message import Message
import asyncio

HOST = "127.0.0.1"
PORT = 65435

setup_logging()
logger = logging.getLogger(__name__)


def setup_demo_data():
    demo_usernames = ["negar", "negin", "aylin", "helen"]

    for uname in demo_usernames:
        demo_user = User(
            username=uname,
            email=f"{uname}@demo.com",
            hashed_password="1234",
            birth_date="2000-01-01",
            gender="Female",
            name=uname.capitalize(),
            phone="+98-912-000-0000",
        )

        user_service.sign_up(demo_user)
        for u in Storage.users:
            if u.username == uname:
                u.is_logged_in = True
                break

    logger.info(
        "*** 4 Demo Users (negar, negin, aylin, helen) Created & Logged In! ***"
    )


async def sign_up(info, writer: asyncio.StreamWriter):
    user = User(**info)  # convert dictionary(**kwargs) to user object with pydantic
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
    writer.write(json.dumps(resp).encode("utf_8"))
    await writer.drain()


async def log_in(info, writer: asyncio.StreamWriter):
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
    writer.write(json.dumps(resp).encode("utf_8"))
    await writer.drain()


async def send_msg(info, writer: asyncio.StreamWriter):
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
    writer.write(json.dumps(resp).encode("utf_8"))
    await writer.drain()


async def inbox(info, writer: asyncio.StreamWriter):
    curr_username = info.get("username")
    curr_user = None
    for u in Storage.users:
        if u.username == curr_username:
            curr_user = u
            break
    if curr_user is None:
        resp = {"status": "error", "message": "User not found!"}
        writer.write(json.dumps(resp).encode("utf_8"))
        await writer.drain()
        return

    messages = message_service.get_messages(curr_user)
    if not messages:
        resp = {
            "status": "success",
            "data": [],
            "message": "Your inbox is empty.",
        }
        writer.write(json.dumps(resp).encode("utf_8"))
        await writer.drain()
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
        writer.write(json.dumps(resp).encode("utf_8"))
        await writer.drain()


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    logger.info(f"Connected by {addr}")
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                logger.info(f"Client {addr} disconnected.")
                break
            text = data.decode("utf_8")
            logger.debug(f"Received raw data from  {addr}: {text}")
            req = json.loads(text)
            command = req.get("command")
            info = req.get("info")

            if command == "SIGN_UP":
                await sign_up(info, writer)
            elif command == "LOG_IN":
                await log_in(info, writer)

            elif command == "SEND_MSG":
                await send_msg(info, writer)

            elif command == "INBOX":
                await inbox(info, writer)
            else:
                error_res = {
                    "status": "error",
                    "message": "Unknown command",
                }
                writer.write(json.dumps(error_res).encode("utf_8"))
                await writer.drain()

    except ConnectionResetError:
        logger.warning(f"Connection reset by client {addr}")
    except Exception as e:
        logger.error(f"Error processing request from {addr}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


async def server_process():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    logger.info(f"AsyncIO Server is listening on {addr}...")
    async with server:
        await server.serve_forever()


def main():
    setup_demo_data()
    asyncio.run(server_process())


if __name__ == "__main__":
    main()
