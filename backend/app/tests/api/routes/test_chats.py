from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import Chat, ChatUpdate, Message, UserCreate
from app.tests.utils.utils import random_email, random_string


def test_create_or_update_chat(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    user = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)

    # Create a new chat
    chat_data = Chat(
        id=random_string(),
        title="Sample chat title",
        path="sample-chat-path",
        user_id=str(user.id),
        messages=[Message(id=random_string(), role="system", content=random_string())],
    )
    response = client.post(
        f"{settings.API_V1_STR}/chats/",
        headers=normal_user_token_headers,
        json=chat_data.model_dump(exclude_unset=True),
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == chat_data.id
    assert content["title"] == chat_data.title
    assert content["path"] == chat_data.path
    assert content["userId"] == str(user.id)
    assert content["messages"] == [
        message.model_dump() for message in chat_data.messages
    ]
    assert content["createdAt"] is not None
    assert content["updatedAt"] is not None

    # Update the existing chat
    update_data = ChatUpdate(
        title="Updated chat title",
        messages=[Message(id=random_string(), role="user", content=random_string())],
    )
    chat_data.title = update_data.title
    chat_data.messages = update_data.messages

    response = client.post(
        f"{settings.API_V1_STR}/chats",
        headers=normal_user_token_headers,
        json=chat_data.model_dump(exclude_unset=True),
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == update_data.title
    assert content["messages"] == [
        message.model_dump() for message in update_data.messages
    ]
    assert content["updatedAt"] is not None


def test_read_chat(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user_in = UserCreate(email=random_email(), password=random_string())
    user = crud.create_user(session=db, user_create=user_in)
    chat_data = Chat(
        id=random_string(),
        title="Sample chat title",
        path="sample-chat-path",
        user_id=str(user.id),
        messages=[Message(id=random_string(), role="system", content=random_string())],
    )
    crud.create_chat(session=db, chat=chat_data)
    response = client.get(
        f"{settings.API_V1_STR}/chats/{chat_data.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == chat_data.id
    assert content["title"] == chat_data.title
    assert content["path"] == chat_data.path
    assert content["userId"] == str(user.id)
    assert content["messages"] == [
        message.model_dump() for message in chat_data.messages
    ]
    assert content["createdAt"] is not None
    assert content["updatedAt"] is not None


def test_read_chat_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/chats/999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Chat not found"


def test_read_chats(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    user = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
    chat_data1 = Chat(
        id=random_string(),
        title="Sample chat title 1",
        path="sample-chat-path-1",
        user_id=str(user.id),
        messages=[Message(id=random_string(), role="system", content=random_string())],
    )
    chat_data2 = Chat(
        id=random_string(),
        title="Sample chat title 2",
        path="sample-chat-path-2",
        user_id=str(user.id),
        messages=[Message(id=random_string(), role="system", content=random_string())],
    )
    crud.create_chat(session=db, chat=chat_data1)
    crud.create_chat(session=db, chat=chat_data2)
    response = client.get(
        f"{settings.API_V1_STR}/chats/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2
    for chat in content["data"]:
        assert chat["userId"] == str(user.id)


def test_update_chat(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    user = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)

    chat_data = Chat(
        id=random_string(),
        title="Sample chat title",
        path="sample-chat-path",
        user_id=str(user.id),
        messages=[Message(id=random_string(), role="system", content=random_string())],
    )
    crud.create_chat(session=db, chat=chat_data)
    update_data = ChatUpdate(
        title="Updated chat title",
        messages=[Message(id=random_string(), role="user", content=random_string())],
    )
    response = client.put(
        f"{settings.API_V1_STR}/chats/{chat_data.id}",
        headers=normal_user_token_headers,
        json=update_data.model_dump(exclude_unset=True),
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == update_data.title
    assert content["messages"] == [
        message.model_dump() for message in update_data.messages
    ]
    assert content["updatedAt"] is not None


def test_update_chat_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    update_data = ChatUpdate(
        title="Updated chat title",
        messages=[Message(id=random_string(), role="user", content=random_string())],
    )
    response = client.put(
        f"{settings.API_V1_STR}/chats/999",
        headers=superuser_token_headers,
        json=update_data.model_dump(exclude_unset=True),
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Chat not found"


def test_delete_chat(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    user = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)

    chat_data = Chat(
        id=random_string(),
        title="Sample chat title",
        path="sample-chat-path",
        user_id=str(user.id),
        messages=[Message(id=random_string(), role="system", content=random_string())],
    )
    crud.create_chat(session=db, chat=chat_data)
    response = client.delete(
        f"{settings.API_V1_STR}/chats/{chat_data.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Chat deleted successfully"


def test_delete_chat_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/chats/999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Chat not found"


def test_delete_all_user_chats(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    user = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)

    chat_data1 = Chat(
        id=random_string(),
        title="Sample chat title 1",
        path="sample-chat-path-1",
        user_id=str(user.id),
        messages=[Message(id=random_string(), role="system", content=random_string())],
    )
    chat_data2 = Chat(
        id=random_string(),
        title="Sample chat title 2",
        path="sample-chat-path-2",
        user_id=str(user.id),
        messages=[Message(id=random_string(), role="system", content=random_string())],
    )
    crud.create_chat(session=db, chat=chat_data1)
    crud.create_chat(session=db, chat=chat_data2)

    response = client.delete(
        f"{settings.API_V1_STR}/chats/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "All chats deleted successfully"

    # Verify that all chats for the user have been deleted
    chats = crud.get_chats(session=db, user_id=str(user.id))
    assert len(chats) == 0
