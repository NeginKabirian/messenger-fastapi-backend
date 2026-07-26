from models.User import User
from models.Message import Message
import services.user_service
import services.message_service
from models.storage import Storage


def show_menu():
    print("Welcome To Messenger System!")
    print("1.sign_up")
    print("2.log_in")
    print("3.send message")
    print("4.show inbox")
    print("5.exit")


def main_menu():
    while True:
        current_user = None
        show_menu()
        cmd = input("\nEnter Command Number> ").strip()
        if cmd == "1":
            print("\n--- Sign Up ---")
            username = input("Username> ").strip()
            email = input("Email> ").strip()
            password = input("Password> ").strip()
            birth_date = input("<birth_date>").strip()
            gender = input("Gender: Male | Female | Prefer not to say")
            Name = input("name> ").strip()
            phone_number = input("Phone Number> ").strip()
            new_user = User(
                id=len(Storage.users) + 1,
                username=username,
                email=email,
                hashed_password=password,
                birth_date=birth_date,
                gender=gender,
                name=Name,
                phone_number=phone_number,
            )
            success = services.user_service.sign_up(new_user)
            if success:
                print(f"Success: User '{username}' signed up successfully!")
            else:
                print("Error: Sign up failed! Username already exists.")
            # log
        elif cmd == "2":
            print("\n--- Log In ---")
            username = input("Username> ").strip()
            password = input("Password> ").strip()

            is_logged_in = services.user_service.login(username, password)

            if is_logged_in:
                print(f"Success: Welcome back, {username}!")
                for u in Storage.users:
                    if u.username == username:
                        current_user = u
                        break
            else:
                print("Error: Invalid username or password!")
            # Todo cmd 3 and 4

        elif cmd == "5":
            print("Goodbye!")
            break
        else:
            print("Error: Invalid command. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main_menu()
