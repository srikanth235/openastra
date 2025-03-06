from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Vote,
    VoteCreate,
    VoteOut,
    VotesOut,
    VoteUpdate,
)

router = APIRouter()


@router.get("/", response_model=VotesOut)
def read_votes(
    session: SessionDep,
    current_user: CurrentUser,
    chat_id: str | None = None,
    message_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve votes. Optionally filter by chat_id and/or message_id.
    """
    # Base query conditions
    conditions = [Vote.user_id == current_user.id]

    # Add filters if provided
    if chat_id:
        conditions.append(Vote.chat_id == chat_id)
    if message_id:
        conditions.append(Vote.message_id == message_id)

    # Get count
    statement = select(func.count()).select_from(Vote).where(*conditions)
    count = session.exec(statement).one()

    # Get votes
    statement = (
        select(Vote)
        .where(*conditions)
        .order_by(Vote.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    votes = session.exec(statement).all()

    # Convert Vote instances to VoteOut instances
    vote_out_list = [VoteOut.model_validate(vote.model_dump()) for vote in votes]
    return VotesOut(data=vote_out_list, count=count)


@router.get("/{id}", response_model=VoteOut)
def read_vote(session: SessionDep, current_user: CurrentUser, id: str) -> VoteOut:
    """
    Get vote by ID.
    """
    vote = session.get(Vote, id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    if not current_user.is_superuser and (vote.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return vote


@router.post("/", response_model=VoteOut)
def create_vote(
    *, session: SessionDep, current_user: CurrentUser, vote_in: VoteCreate
) -> Any:
    """
    Create new vote or update existing one.
    """
    # Check if user already has a vote for this message
    existing_vote = session.exec(
        select(Vote).where(
            Vote.user_id == current_user.id,
            Vote.chat_id == vote_in.chat_id,
            Vote.message_id == vote_in.message_id,
        )
    ).first()

    if existing_vote:
        # Update existing vote
        existing_vote.is_upvoted = vote_in.is_upvoted
        session.add(existing_vote)
        session.commit()
        session.refresh(existing_vote)
        return existing_vote

    # Create new vote
    vote = Vote.model_validate(vote_in, update={"user_id": current_user.id})
    session.add(vote)
    session.commit()
    session.refresh(vote)
    return vote


@router.put("/{id}", response_model=VoteOut)
def update_vote(
    *, session: SessionDep, current_user: CurrentUser, id: str, vote_in: VoteUpdate
) -> Any:
    """
    Update vote.
    """
    vote = session.get(Vote, id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    if not current_user.is_superuser and (vote.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = vote_in.model_dump(exclude_unset=True)
    vote.sqlmodel_update(update_dict)
    session.add(vote)
    session.commit()
    session.refresh(vote)
    return vote


@router.delete("/{id}")
def delete_vote(session: SessionDep, current_user: CurrentUser, id: str) -> Message:
    """
    Delete vote.
    """
    vote = session.get(Vote, id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    if not current_user.is_superuser and (vote.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(vote)
    session.commit()
    return Message(message="Vote deleted successfully")
