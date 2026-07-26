from models.User import User
from models.storage import Storage
def sign_up(new_user: User)->bool:
    for user in Storage.users:
         # hash function will be add later
        if user.username == new_user.username:
            return False
    Storage.users.append(new_user)
    # log 
    return True
def login(username:str , password:str)-> User | None:
    for user in  Storage.users:
        if user.username == username:
            # hash function will be add later
            if user.hashed_password == password:
                user.is_logged_in = True
                # log
                return user
        
    return None

