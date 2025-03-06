from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.vote import Vote


def test_create_vote(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create a vote
    data = {
        "chat_id": "test-chat-id",
        "message_id": "test-message-id",
        "is_upvoted": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/votes/", headers=superuser_token_headers, json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["chatId"] == data["chat_id"]
    assert content["messageId"] == data["message_id"]
    assert content["isUpvoted"] == data["is_upvoted"]
    assert "id" in content
    assert "userId" in content


def test_update_existing_vote(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create a vote
    data = {
        "chat_id": "test-chat-id-update",
        "message_id": "test-message-id-update",
        "is_upvoted": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/votes/", headers=superuser_token_headers, json=data
    )
    vote_id = response.json()["id"]

    # Create another vote with the same chat_id and message_id but different is_upvoted
    update_data = {
        "chat_id": "test-chat-id-update",
        "message_id": "test-message-id-update",
        "is_upvoted": False,
    }
    response = client.post(
        f"{settings.API_V1_STR}/votes/",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == vote_id  # Should be the same vote
    assert content["isUpvoted"] == update_data["is_upvoted"]  # Should be updated


def test_read_vote(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create a vote
    data = {
        "chat_id": "test-chat-id-read",
        "message_id": "test-message-id-read",
        "is_upvoted": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/votes/", headers=superuser_token_headers, json=data
    )
    vote_id = response.json()["id"]

    # Read the vote
    response = client.get(
        f"{settings.API_V1_STR}/votes/{vote_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["chatId"] == data["chat_id"]
    assert content["messageId"] == data["message_id"]
    assert content["isUpvoted"] == data["is_upvoted"]
    assert content["id"] == vote_id


def test_read_votes(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create multiple votes
    chat_id = "test-chat-id-multiple"
    for i in range(3):
        data = {
            "chat_id": chat_id,
            "message_id": f"test-message-id-{i}",
            "is_upvoted": i % 2 == 0,  # Alternate between True and False
        }
        client.post(
            f"{settings.API_V1_STR}/votes/", headers=superuser_token_headers, json=data
        )

    # Read all votes
    response = client.get(
        f"{settings.API_V1_STR}/votes/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert content["count"] >= 3
    assert len(content["data"]) >= 3


def test_update_vote(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create a vote
    data = {
        "chat_id": "test-chat-id-update-api",
        "message_id": "test-message-id-update-api",
        "is_upvoted": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/votes/", headers=superuser_token_headers, json=data
    )
    vote_id = response.json()["id"]

    # Update the vote
    update_data = {
        "is_upvoted": False,
    }
    response = client.put(
        f"{settings.API_V1_STR}/votes/{vote_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["isUpvoted"] == update_data["is_upvoted"]
    assert content["id"] == vote_id


def test_delete_vote(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create a vote
    data = {
        "chat_id": "test-chat-id-delete",
        "message_id": "test-message-id-delete",
        "is_upvoted": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/votes/", headers=superuser_token_headers, json=data
    )
    vote_id = response.json()["id"]

    # Delete the vote
    response = client.delete(
        f"{settings.API_V1_STR}/votes/{vote_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify vote is deleted
    response = client.get(
        f"{settings.API_V1_STR}/votes/{vote_id}", headers=superuser_token_headers
    )
    assert response.status_code == 404


def test_filter_votes_by_chat_and_message(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Clean up any existing votes first
    _db.query(Vote).delete()
    _db.commit()

    # Create votes for different chats and messages
    chat_id1 = "test-chat-id-filter-1"
    chat_id2 = "test-chat-id-filter-2"

    # Create votes for chat 1
    for i in range(2):
        data = {
            "chat_id": chat_id1,
            "message_id": f"test-message-id-{i}",
            "is_upvoted": True,
        }
        client.post(
            f"{settings.API_V1_STR}/votes/", headers=superuser_token_headers, json=data
        )

    # Create votes for chat 2
    for i in range(3):
        data = {
            "chat_id": chat_id2,
            "message_id": f"test-message-id-{i}",
            "is_upvoted": False,
        }
        client.post(
            f"{settings.API_V1_STR}/votes/", headers=superuser_token_headers, json=data
        )

    # Filter votes by chat_id1
    response = client.get(
        f"{settings.API_V1_STR}/votes/?chat_id={chat_id1}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 2
    assert len(content["data"]) == 2
    for vote in content["data"]:
        assert vote["chatId"] == chat_id1

    # Filter votes by chat_id2
    response = client.get(
        f"{settings.API_V1_STR}/votes/?chat_id={chat_id2}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 3
    assert len(content["data"]) == 3
    for vote in content["data"]:
        assert vote["chatId"] == chat_id2

    # Filter votes by specific message_id
    specific_message_id = "test-message-id-1"
    response = client.get(
        f"{settings.API_V1_STR}/votes/?message_id={specific_message_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 2  # One from each chat
    assert len(content["data"]) == 2
    for vote in content["data"]:
        assert vote["messageId"] == specific_message_id

    # Filter by both chat_id and message_id
    response = client.get(
        f"{settings.API_V1_STR}/votes/?chat_id={chat_id1}&message_id={specific_message_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert len(content["data"]) == 1
    assert content["data"][0]["chatId"] == chat_id1
    assert content["data"][0]["messageId"] == specific_message_id
