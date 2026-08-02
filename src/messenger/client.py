from messenger.models.User import User
from messenger.models.Message import Message
from pydantic import ValidationError
import getpass
from messenger.core.logger import setup_logging
import logging
import socket
import json

setup_logging()
logger = logging.getLogger(__name__)
HOST = "127.0.0.1"
PORT = 65435


def show_menu():
    print("\n" + "=" * 30)
    print("Welcome To Messenger System!")
    print("1.sign_up")
    print("2.log_in")
    print("3.send message")
    print("4.show inbox")
    print("5.exit")
    print("\n" + "=" * 30)


def main_menu():
    s = socket.socket()
    s.connect((HOST, PORT))
    while True:
        show_menu()
        cmd = input("Enter Command Number> ").strip()
        if cmd == "1":
            print("\n--- Sign Up ---")
            username = input("Username> ").strip()
            email = input("Email> ").strip()
            password = getpass.getpass("Password> ").strip()
            confirm_password = getpass.getpass("Confirm Password> ").strip()

            if password != confirm_password:
                logger.error("Passwords do not match!")
                continue
            birth_date = input("<birth_date>(eg.2005-01-30)").strip()
            gender = input("Gender: Male | Female | Prefer not to say: ")
            Name = input("name> ").strip()
            phone = input("Phone Number>(eg.+1-650-253-0000) ").strip()
            try:
                new_user = User(
                    username=username,
                    email=email,
                    hashed_password=password,
                    birth_date=birth_date,
                    gender=gender,
                    name=Name,
                    phone=phone,
                )
                info = new_user.model_dump(
                    mode="json"
                )  # convert object to json dictionary with pydantic
                req_data = {"command": "SIGN_UP", "info": info}
                s.sendall(json.dumps(req_data).encode("utf_8"))
                resp_bytes = s.recv(4096).decode("utf_8")
                resp = json.loads(resp_bytes)
                if resp["status"] == "success":
                    logger.info(f"Success:{resp['message']}")
                else:
                    logger.error(f"Error: {resp['message']}")
            except ValidationError as e:
                logger.error("Invalid Data!")
                for error in e.errors():
                    logger.error(f"- {error['loc'][0]}: {error['msg']}")
        elif cmd == "2":
            print("\n--- Log In ---")
            username = input("Username> ").strip()
            password = getpass.getpass("Password> ").strip()
            info = {"username": username, "password": password}
            req_data = {"command": "LOG_IN", "info": info}
            s.sendall(json.dumps(req_data).encode("utf_8"))
            resp_bytes = s.recv(4096).decode("utf_8")
            resp = json.loads(resp_bytes)
            if resp["status"] == "success":
                logger.info(f"Success:{resp['message']}")
            else:
                logger.error(f"Error:{resp['message']}")
        elif cmd == "3":
            print("\n--- Send Message ---")
            sender_username = input("Enter your username> ").strip()
            receiver_usernames = []
            stop = False
            while stop == False:
                receiver_usernames.append(input("Enter receiver username> ").strip())
                check = input(
                    "continue to input receiver_username?(yes or no) ".strip()
                )
                if check == "no":
                    stop = True
            content = input("Enter message content> ").strip()
            info = {
                "curr_username": sender_username,
                "recv_usernames": receiver_usernames,
                "content": content,
            }
            req_data = {"command": "SEND_MSG", "info": info}
            s.sendall(json.dumps(req_data).encode("utf_8"))
            resp_bytes = s.recv(4096).decode("utf_8")
            resp = json.loads(resp_bytes)

            if resp["status"] == "success":
                logger.info(f"Success:{resp['message']}")
            else:
                logger.error(f"Error: {resp['message']}")
        elif cmd == "4":
            print("\n--- Inbox ---")
            username = input("Enter your username> ").strip()
            info = {"username": username}
            req_data = {"command": "INBOX", "info": info}
            s.sendall(json.dumps(req_data).encode("utf_8"))
            resp_bytes = s.recv(4096).decode("utf_8")
            resp = json.loads(resp_bytes)

            if resp["status"] == "success":
                logger.info(f"Success:{resp['message']}")
                if len(resp.get("data", [])) == 0:
                    print(resp.get("message", "Inbox is empty."))
                else:
                    for msg in resp["data"]:
                        print(msg)
        elif cmd == "5":
            print("Goodbye!")
            break
        else:
            logger.error("Invalid command. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main_menu()
