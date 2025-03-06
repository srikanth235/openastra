from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Document,
    DocumentCreate,
    DocumentOut,
    DocumentsOut,
    DocumentUpdate,
    Message,
)

router = APIRouter()


@router.get("/", response_model=DocumentsOut)
def read_documents(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve documents. Optionally filter by project_id.
    """
    # Base query conditions
    conditions = [Document.user_id == current_user.id]

    # Add project filter if provided
    if project_id:
        conditions.append(Document.project_id == project_id)

    # Get count
    statement = select(func.count()).select_from(Document).where(*conditions)
    count = session.exec(statement).one()

    # Get documents
    statement = (
        select(Document)
        .where(*conditions)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = session.exec(statement).all()

    # Convert Document instances to DocumentOut
    documents_out = [DocumentOut.model_validate(doc.model_dump()) for doc in documents]

    return DocumentsOut(data=documents_out, count=count)


@router.get("/{id}", response_model=DocumentOut)
def read_document(
    session: SessionDep, current_user: CurrentUser, id: str
) -> DocumentOut:
    """
    Get document by ID.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_superuser and (document.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return document


@router.post("/", response_model=DocumentOut)
def create_document(
    *, session: SessionDep, current_user: CurrentUser, document_in: DocumentCreate
) -> Any:
    """
    Create new document.
    """
    document = Document.model_validate(document_in, update={"user_id": current_user.id})
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.put("/{id}", response_model=DocumentOut)
def update_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: str,
    document_in: DocumentUpdate,
) -> Any:
    """
    Update document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_superuser and (document.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = document_in.model_dump(exclude_unset=True)
    document.sqlmodel_update(update_dict)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.delete("/{id}")
def delete_document(session: SessionDep, current_user: CurrentUser, id: str) -> Message:
    """
    Delete document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_superuser and (document.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(document)
    session.commit()
    return Message(message="Document deleted successfully")
