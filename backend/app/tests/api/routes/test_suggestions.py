from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import DocumentKind


def test_create_suggestion(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # First create a document
    doc_data = {
        "title": "Test Document for Suggestion",
        "content": "This is a test document content for suggestion",
        "kind": DocumentKind.TEXT,
    }
    doc_response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        json=doc_data,
    )
    document_id = doc_response.json()["id"]

    # Create a suggestion
    data = {
        "document_id": document_id,
        "original_text": "test document content",
        "suggested_text": "improved document content",
        "description": "This is a better wording",
    }
    response = client.post(
        f"{settings.API_V1_STR}/suggestions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["documentId"] == data["document_id"]
    assert content["originalText"] == data["original_text"]
    assert content["suggestedText"] == data["suggested_text"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "userId" in content


def test_read_suggestion(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # First create a document
    doc_data = {
        "title": "Test Document for Reading Suggestion",
        "content": "This is a test document content for reading suggestion",
        "kind": DocumentKind.TEXT,
    }
    doc_response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        json=doc_data,
    )
    document_id = doc_response.json()["id"]

    # Create a suggestion
    data = {
        "document_id": document_id,
        "original_text": "test document content",
        "suggested_text": "improved document content",
        "description": "This is a better wording",
    }
    response = client.post(
        f"{settings.API_V1_STR}/suggestions/",
        headers=superuser_token_headers,
        json=data,
    )
    suggestion_id = response.json()["id"]

    # Read the suggestion
    response = client.get(
        f"{settings.API_V1_STR}/suggestions/{suggestion_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["documentId"] == data["document_id"]
    assert content["originalText"] == data["original_text"]
    assert content["suggestedText"] == data["suggested_text"]
    assert content["description"] == data["description"]
    assert content["id"] == suggestion_id


def test_read_suggestions(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # First create a document
    doc_data = {
        "title": "Test Document for Multiple Suggestions",
        "content": "This is a test document content for multiple suggestions",
        "kind": DocumentKind.TEXT,
    }
    doc_response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        json=doc_data,
    )
    document_id = doc_response.json()["id"]

    # Create multiple suggestions
    for i in range(3):
        data = {
            "document_id": document_id,
            "original_text": f"test document content {i}",
            "suggested_text": f"improved document content {i}",
            "description": f"This is a better wording {i}",
        }
        client.post(
            f"{settings.API_V1_STR}/suggestions/",
            headers=superuser_token_headers,
            json=data,
        )

    # Read all suggestions
    response = client.get(
        f"{settings.API_V1_STR}/suggestions/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert content["count"] >= 3
    assert len(content["data"]) >= 3


def test_update_suggestion(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # First create a document
    doc_data = {
        "title": "Test Document for Updating Suggestion",
        "content": "This is a test document content for updating suggestion",
        "kind": DocumentKind.TEXT,
    }
    doc_response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        json=doc_data,
    )
    document_id = doc_response.json()["id"]

    # Create a suggestion
    data = {
        "document_id": document_id,
        "original_text": "test document content",
        "suggested_text": "improved document content",
        "description": "This is a better wording",
        "is_resolved": False,
    }
    response = client.post(
        f"{settings.API_V1_STR}/suggestions/",
        headers=superuser_token_headers,
        json=data,
    )
    suggestion_id = response.json()["id"]

    # Update the suggestion
    update_data = {
        "suggested_text": "even better document content",
        "description": "This is an even better wording",
        "is_resolved": True,
    }
    response = client.put(
        f"{settings.API_V1_STR}/suggestions/{suggestion_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["suggestedText"] == update_data["suggested_text"]
    assert content["description"] == update_data["description"]
    assert content["isResolved"] == update_data["is_resolved"]
    assert content["id"] == suggestion_id


def test_delete_suggestion(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # First create a document
    doc_data = {
        "title": "Test Document for Deleting Suggestion",
        "content": "This is a test document content for deleting suggestion",
        "kind": DocumentKind.TEXT,
    }
    doc_response = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        json=doc_data,
    )
    document_id = doc_response.json()["id"]

    # Create a suggestion
    data = {
        "document_id": document_id,
        "original_text": "test document content",
        "suggested_text": "improved document content",
        "description": "This is a better wording",
    }
    response = client.post(
        f"{settings.API_V1_STR}/suggestions/",
        headers=superuser_token_headers,
        json=data,
    )
    suggestion_id = response.json()["id"]

    # Delete the suggestion
    response = client.delete(
        f"{settings.API_V1_STR}/suggestions/{suggestion_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    # Verify suggestion is deleted
    response = client.get(
        f"{settings.API_V1_STR}/suggestions/{suggestion_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_filter_suggestions_by_document(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create two documents
    doc_data1 = {
        "title": "Test Document 1 for Filtering",
        "content": "This is test document 1 content for filtering",
        "kind": DocumentKind.TEXT,
    }
    doc_response1 = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        json=doc_data1,
    )
    document_id1 = doc_response1.json()["id"]

    doc_data2 = {
        "title": "Test Document 2 for Filtering",
        "content": "This is test document 2 content for filtering",
        "kind": DocumentKind.TEXT,
    }
    doc_response2 = client.post(
        f"{settings.API_V1_STR}/documents/",
        headers=superuser_token_headers,
        json=doc_data2,
    )
    document_id2 = doc_response2.json()["id"]

    # Create suggestions for document 1
    for i in range(2):
        data = {
            "document_id": document_id1,
            "original_text": f"test document 1 content {i}",
            "suggested_text": f"improved document 1 content {i}",
            "description": f"This is a better wording for doc 1 - {i}",
        }
        client.post(
            f"{settings.API_V1_STR}/suggestions/",
            headers=superuser_token_headers,
            json=data,
        )

    # Create suggestions for document 2
    for i in range(3):
        data = {
            "document_id": document_id2,
            "original_text": f"test document 2 content {i}",
            "suggested_text": f"improved document 2 content {i}",
            "description": f"This is a better wording for doc 2 - {i}",
        }
        client.post(
            f"{settings.API_V1_STR}/suggestions/",
            headers=superuser_token_headers,
            json=data,
        )

    # Filter suggestions by document_id1
    response = client.get(
        f"{settings.API_V1_STR}/suggestions/?document_id={document_id1}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 2
    assert len(content["data"]) == 2
    for suggestion in content["data"]:
        assert suggestion["documentId"] == document_id1

    # Filter suggestions by document_id2
    response = client.get(
        f"{settings.API_V1_STR}/suggestions/?document_id={document_id2}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 3
    assert len(content["data"]) == 3
    for suggestion in content["data"]:
        assert suggestion["documentId"] == document_id2
