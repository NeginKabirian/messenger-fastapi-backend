import pytest
from pydantic import ValidationError
from messenger.models.User import User
from messenger.models.storage import Storage
import messenger.services.user_service as user_service


@pytest.fixture(autouse=True)
def clean():
    Storage.users.clear()


def create_test_user(username: str) -> User:
    return User(
        username=username,
        email=f"{username}@gmail.com",
        hashed_password="1234",
        birth_date="2005-01-22",
        gender="Prefer not to say",
        name=username,
        phone="+98-913-700-2169",
    )


def test_sign_up_success():
    new_user = create_test_user("Neginka0")
    res = user_service.sign_up(new_user)
    assert res is True
    assert len(Storage.users) == 1
    assert Storage.users[0].username == "Neginka0"


def test_sign_up_duplicate_username():
    userA = create_test_user("Neginka0")
    userB = create_test_user("Neginka0")
    resA = user_service.sign_up(userA)
    resB = user_service.sign_up(userB)
    assert resA is True and resB is False
    assert len(Storage.users) == 1


def sign_up_wrong_information_birthday_user():

    with pytest.raises(ValidationError):
        User(
            username="Neginka0",
            email="Neginka0@gmail.com",
            hashed_password="1234",
            birth_date="2005-01",
            gender="Prefer not to say",
        )


def sign_up_wrong_information_gmail_user():
    with pytest.raises(ValidationError):
        User(
            username="Neginka0",
            email="Neginka0",
            hashed_password="1234",
            birth_date="2005-01-22",
            gender="Prefer not to say",
        )


def sign_up_wrong_gender_user():
    with pytest.raises(ValidationError):
        User(
            username="Neginka0",
            email="Neginka0@gmail.com",
            hashed_password="1234",
            birth_date="2005-01-22",
            gender="alaki",
        )


def test_login_success():
    new_user = create_test_user("Neginka0")
    user_service.sign_up(new_user)
    res = user_service.login("Neginka0", "1234")
    assert res is not None
    assert res == new_user
    assert res.is_logged_in == True
    assert res.username == "Neginka0"


def test_login_wrong_password():
    new_user = create_test_user("Neginka0")
    user_service.sign_up(new_user)
    res = user_service.login("Neginka0", "salam")
    assert res is None
    assert new_user.is_logged_in is False
