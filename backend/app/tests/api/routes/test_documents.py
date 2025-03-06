from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import DocumentKind


def test_create_document(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    data = {
        "title": "Test Document",
        "content": "This is a test document content",
        "kind": DocumentKind.TEXT,
    }
    response = client.post(
        f"{settings.API_V1_STR}/documents/", headers=superuser_token_headers, json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["content"] == data["content"]
    assert content["kind"] == data["kind"]
    assert "id" in content
    assert "userId" in content


def test_read_document(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create a document
    data = {
        "title": "Test Document for Reading",
        "content": "This is a test document content for reading",
        "kind": DocumentKind.TEXT,
    }
    response = client.post(
        f"{settings.API_V1_STR}/documents/", headers=superuser_token_headers, json=data
    )
    document_id = response.json()["id"]

    # Read the document
    response = client.get(
        f"{settings.API_V1_STR}/documents/{document_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["content"] == data["content"]
    assert content["kind"] == data["kind"]
    assert content["id"] == document_id


def test_read_documents(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create multiple documents
    for i in range(3):
        data = {
            "title": f"Test Document {i}",
            "content": f"This is test document content {i}",
            "kind": DocumentKind.TEXT,
        }
        client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            json=data,
        )

    # Read all documents
    response = client.get(
        f"{settings.API_V1_STR}/documents/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert content["count"] >= 3
    assert len(content["data"]) >= 3


def test_update_document(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create a document
    data = {
        "title": "Test Document for Update",
        "content": "This is a test document content for update",
        "kind": DocumentKind.TEXT,
    }
    response = client.post(
        f"{settings.API_V1_STR}/documents/", headers=superuser_token_headers, json=data
    )
    document_id = response.json()["id"]

    # Update the document
    update_data = {
        "title": "Updated Test Document",
        "content": "This is updated test document content",
        "kind": DocumentKind.CODE,
    }
    response = client.put(
        f"{settings.API_V1_STR}/documents/{document_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == update_data["title"]
    assert content["content"] == update_data["content"]
    assert content["kind"] == update_data["kind"]
    assert content["id"] == document_id


def test_delete_document(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create a document
    data = {
        "title": "Test Document for Deletion",
        "content": "This is a test document content for deletion",
        "kind": DocumentKind.TEXT,
    }
    response = client.post(
        f"{settings.API_V1_STR}/documents/", headers=superuser_token_headers, json=data
    )
    document_id = response.json()["id"]

    # Delete the document
    response = client.delete(
        f"{settings.API_V1_STR}/documents/{document_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    # Verify document is deleted
    response = client.get(
        f"{settings.API_V1_STR}/documents/{document_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_filter_documents_by_project(
    client: TestClient, superuser_token_headers: dict, _db: Session
) -> None:
    # Create a project first
    project_data = {
        "title": "Test Project for Documents",
        "description": "Project for testing document filtering",
        "model": "gpt-4",
    }
    project_response = client.post(
        f"{settings.API_V1_STR}/projects/",
        headers=superuser_token_headers,
        json=project_data,
    )
    print("Project response:", project_response.status_code, project_response.json())
    project_id = project_response.json()["id"]

    # Create documents with project_id
    for i in range(2):
        data = {
            "title": f"Project Document {i}",
            "content": f"This is project document content {i}",
            "kind": DocumentKind.TEXT,
            "project_id": project_id,
        }
        client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            json=data,
        )

    # Create documents without project_id
    for i in range(2):
        data = {
            "title": f"Non-Project Document {i}",
            "content": f"This is non-project document content {i}",
            "kind": DocumentKind.TEXT,
        }
        client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            json=data,
        )

    # Filter documents by project_id
    response = client.get(
        f"{settings.API_V1_STR}/documents/?project_id={project_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 2
    assert len(content["data"]) == 2
    for doc in content["data"]:
        assert doc["projectId"] == project_id
        assert "Project Document" in doc["title"]
