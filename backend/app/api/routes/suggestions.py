from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Suggestion,
    SuggestionCreate,
    SuggestionOut,
    SuggestionsOut,
    SuggestionUpdate,
)

router = APIRouter()


@router.get("/", response_model=SuggestionsOut)
def read_suggestions(
    session: SessionDep,
    current_user: CurrentUser,
    document_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve suggestions. Optionally filter by document_id.
    """
    # Base query conditions
    conditions = [Suggestion.user_id == current_user.id]

    # Add document filter if provided
    if document_id:
        conditions.append(Suggestion.document_id == document_id)

    # Get count
    statement = select(func.count()).select_from(Suggestion).where(*conditions)
    count = session.exec(statement).one()

    # Get suggestions
    statement = (
        select(Suggestion)
        .where(*conditions)
        .order_by(Suggestion.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    suggestions = session.exec(statement).all()

    # Convert Suggestion models to SuggestionOut models
    suggestions_out = [SuggestionOut(**s.model_dump()) for s in suggestions]

    return SuggestionsOut(data=suggestions_out, count=count)


@router.get("/{id}", response_model=SuggestionOut)
def read_suggestion(
    session: SessionDep, current_user: CurrentUser, id: str
) -> SuggestionOut:
    """
    Get suggestion by ID.
    """
    suggestion = session.get(Suggestion, id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    if not current_user.is_superuser and (suggestion.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return suggestion


@router.post("/", response_model=SuggestionOut)
def create_suggestion(
    *, session: SessionDep, current_user: CurrentUser, suggestion_in: SuggestionCreate
) -> Any:
    """
    Create new suggestion.
    """
    suggestion = Suggestion.model_validate(
        suggestion_in, update={"user_id": current_user.id}
    )
    session.add(suggestion)
    session.commit()
    session.refresh(suggestion)
    return suggestion


@router.put("/{id}", response_model=SuggestionOut)
def update_suggestion(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: str,
    suggestion_in: SuggestionUpdate,
) -> Any:
    """
    Update suggestion.
    """
    suggestion = session.get(Suggestion, id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    if not current_user.is_superuser and (suggestion.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = suggestion_in.model_dump(exclude_unset=True)
    suggestion.sqlmodel_update(update_dict)
    session.add(suggestion)
    session.commit()
    session.refresh(suggestion)
    return suggestion


@router.delete("/{id}")
def delete_suggestion(
    session: SessionDep, current_user: CurrentUser, id: str
) -> Message:
    """
    Delete suggestion.
    """
    suggestion = session.get(Suggestion, id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    if not current_user.is_superuser and (suggestion.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(suggestion)
    session.commit()
    return Message(message="Suggestion deleted successfully")
