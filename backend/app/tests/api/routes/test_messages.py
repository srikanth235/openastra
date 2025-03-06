import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.models.message import Message


def test_create_message(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    # Create a unique chat_id for this test run
    chat_id = f"test-chat-id-{uuid.uuid4()}"

    try:
        # Create a message
        data = {
            "role": "user",
            "content": "Hello, world!",
        }
        response = client.post(
            f"{settings.API_V1_STR}/messages/?chat_id={chat_id}",
            headers=superuser_token_headers,
            json=data,
        )
        assert response.status_code == 200
        content = response.json()
        assert content["role"] == data["role"]
        assert content["content"] == data["content"]
        assert content["chatId"] == chat_id
        assert "id" in content
        assert "createdAt" in content

        # No need to store message_id as it's not used for cleanup
        # We're cleaning up by chat_id instead

    finally:
        # Clean up the message created by this test
        statement = delete(Message).where(Message.chat_id == chat_id)
        db.execute(statement)
        db.commit()


def test_read_message(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    # Create a unique chat_id for this test run
    chat_id = f"test-chat-id-read-{uuid.uuid4()}"

    try:
        # Create a message
        data = {
            "role": "user",
            "content": "Test message for reading",
        }
        response = client.post(
            f"{settings.API_V1_STR}/messages/?chat_id={chat_id}",
            headers=superuser_token_headers,
            json=data,
        )
        message_id = response.json()["id"]

        # Read the message
        response = client.get(
            f"{settings.API_V1_STR}/messages/{message_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        content = response.json()
        assert content["role"] == data["role"]
        assert content["content"] == data["content"]
        assert content["chatId"] == chat_id
        assert content["id"] == message_id

    finally:
        # Clean up the message created by this test
        statement = delete(Message).where(Message.chat_id == chat_id)
        db.execute(statement)
        db.commit()


def test_read_messages(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    # Create a unique chat_id for this test run
    chat_id = f"test-chat-id-multiple-{uuid.uuid4()}"

    try:
        # Create multiple messages
        for i in range(3):
            data = {
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Test message {i}",
            }
            client.post(
                f"{settings.API_V1_STR}/messages/?chat_id={chat_id}",
                headers=superuser_token_headers,
                json=data,
            )

        # Read all messages
        response = client.get(
            f"{settings.API_V1_STR}/messages/", headers=superuser_token_headers
        )
        assert response.status_code == 200
        content = response.json()
        assert "data" in content
        assert "count" in content
        assert content["count"] >= 3
        assert len(content["data"]) >= 3

        # Filter messages by chat_id
        response = client.get(
            f"{settings.API_V1_STR}/messages/?chat_id={chat_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        content = response.json()
        assert content["count"] == 3
        assert len(content["data"]) == 3
        for message in content["data"]:
            assert message["chatId"] == chat_id

    finally:
        # Clean up the messages created by this test
        statement = delete(Message).where(Message.chat_id == chat_id)
        db.execute(statement)
        db.commit()


def test_delete_message(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    # Create a unique chat_id for this test run
    chat_id = f"test-chat-id-delete-{uuid.uuid4()}"

    try:
        # Create a message
        data = {
            "role": "user",
            "content": "Message to be deleted",
        }
        response = client.post(
            f"{settings.API_V1_STR}/messages/?chat_id={chat_id}",
            headers=superuser_token_headers,
            json=data,
        )
        message_id = response.json()["id"]

        # Delete the message
        response = client.delete(
            f"{settings.API_V1_STR}/messages/{message_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Message deleted successfully"

        # Verify message is deleted
        response = client.get(
            f"{settings.API_V1_STR}/messages/{message_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 404

    finally:
        # Clean up any remaining messages (should be none after deletion)
        statement = delete(Message).where(Message.chat_id == chat_id)
        db.execute(statement)
        db.commit()


def test_normal_user_cannot_delete_message(
    client: TestClient,
    normal_user_token_headers: dict,
    superuser_token_headers: dict,
    db: Session,
) -> None:
    # Create a unique chat_id for this test run
    chat_id = f"test-chat-id-permissions-{uuid.uuid4()}"

    try:
        # Create a message as superuser
        data = {
            "role": "user",
            "content": "Message that normal user shouldn't delete",
        }
        response = client.post(
            f"{settings.API_V1_STR}/messages/?chat_id={chat_id}",
            headers=superuser_token_headers,
            json=data,
        )
        message_id = response.json()["id"]

        # Try to delete the message as normal user
        response = client.delete(
            f"{settings.API_V1_STR}/messages/{message_id}",
            headers=normal_user_token_headers,
        )
        assert response.status_code == 400
        assert "Not enough permissions" in response.json()["detail"]

        # Verify message still exists
        response = client.get(
            f"{settings.API_V1_STR}/messages/{message_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200

    finally:
        # Clean up the message created by this test
        statement = delete(Message).where(Message.chat_id == chat_id)
        db.execute(statement)
        db.commit()
