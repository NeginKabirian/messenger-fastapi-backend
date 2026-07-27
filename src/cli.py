from models.User import User
from models.Message import Message
import services.user_service
import services.message_service
from models.storage import Storage
from pydantic import ValidationError
import getpass

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
    current_user = None
    while True:
        show_menu()
        cmd = input("\nEnter Command Number> ").strip()
        if cmd == "1":
            print("\n--- Sign Up ---")
            username = input("Username> ").strip()
            email = input("Email> ").strip()
            password = getpass.getpass("Password> ").strip()
            confirm_password = getpass.getpass("Confirm Password> ").strip()
    
            if password != confirm_password:
                print("Error: Passwords do not match!")
                continue

            birth_date = input("<birth_date>(eg.2005-01-30)").strip()
            gender = input("Gender: Male | Female | Prefer not to say: ")
            Name = input("name> ").strip()
            phone = input("Phone Number>(eg.+1-650-253-0000) ").strip()
            try:
                new_user = User(
                    id=len(Storage.users) + 1,
                    username=username,
                    email=email,
                    hashed_password=password,
                    birth_date=birth_date,
                    gender=gender,
                    name=Name,
                    phone=phone,
                )
                success = services.user_service.sign_up(new_user)
                if success:
                    print(f"Success: User '{username}' signed up successfully!")
                else:
                    print("Error: Sign up failed! Username already exists.")
                # log
            except ValidationError as e:
                print("\nError: Invalid Data!")
                for error in e.errors():
                    print(f"- {error['loc'][0]}: {error['msg']}")
        elif cmd == "2":
            print("\n--- Log In ---")
            username = input("Username> ").strip()
            password = getpass.getpass("Password> ").strip()

            logged_in_user = services.user_service.login(username, password)

            if logged_in_user:
                current_user = logged_in_user
                print(f"Success: Welcome back, {current_user.username}!")
            else:
                print("Error: Invalid username or password!")

            # Todo cmd 3 and 4
        elif cmd == "3":
            print("\n--- Send Message ---")
            if current_user is None:
                print("Error: You must log in first to send a message.")
                continue
            receiver_username = input("Enter receiver username> ").strip()
            receiver_user = None
            for u in Storage.users:
                if u.username == receiver_username:
                    receiver_user = u
                    break
            if receiver_user is None:
                print("Error: Receiver user not found!")
                continue
            content = input("Enter message content> ").strip()
            new_message = Message(
                sender=current_user, receiver=[receiver_user], content=content
            )
            services.message_service.send_message(new_message)
            print("Success: Message sent successfully!")
        elif cmd == "4":
            print("\n--- Inbox ---")
            if current_user is None:
                print("Error: You must log in first to view your inbox.")
                continue
            user_messages = services.message_service.get_messages(current_user)
            if not user_messages:
                print("Your inbox is empty.")
            else:
                for msg in user_messages:
                    print(
                        f"From: {msg.sender.username} | Text: {msg.content} | Time: {msg.created_at.strftime('%H:%M')}"
                    )

        elif cmd == "5":
            print("Goodbye!")
            break
        else:
            print("Error: Invalid command. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main_menu()
