import pytest
from messenger.models.User import User
from messenger.models.storage import Storage
from messenger.models.Message import Message
import messenger.services.message_service as message_service


@pytest.fixture(autouse=True)
def clean():
    Storage.users.clear()
    Storage.messages.clear()


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


def test_send_recv_messages():
    A = create_test_user("Neginka0")
    B = create_test_user("Shadi")
    C = create_test_user("Gazala")
    D = create_test_user("Adly")

    Storage.users.extend([A, B, C, D])

    msg1 = Message(sender=A, receiver=[B], content="Hello Shaaaaaaaaadi!")
    msg2 = Message(sender=A, receiver=[B, C, D], content="Posht Comp :)))")
    message_service.send_message(msg1)
    message_service.send_message(msg2)
    assert len(Storage.messages) == 2

    B_inbox = message_service.get_messages(B)
    assert len(B_inbox) == 2
    assert B_inbox[0].content == "Hello Shaaaaaaaaadi!"
    assert B_inbox[1].content == "Posht Comp :)))"

    A_inbox = message_service.get_messages(A)
    assert len(A_inbox) == 2
    assert A_inbox[0].content == "Hello Shaaaaaaaaadi!"
    assert A_inbox[1].content == "Posht Comp :)))"

    C_inbox = message_service.get_messages(C)
    assert len(C_inbox) == 1
    assert C_inbox[0].content == "Posht Comp :)))"

    D_inbox = message_service.get_messages(D)
    assert len(D_inbox) == 1
    assert D_inbox[0].content == "Posht Comp :)))"
