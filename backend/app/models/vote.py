from datetime import datetime

import nanoid
from sqlalchemy import DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from .base import CamelModel
from .user import User


class VoteBase(CamelModel):
    chat_id: str
    message_id: str
    is_upvoted: bool


class VoteCreate(VoteBase):
    pass


class VoteUpdate(CamelModel):
    is_upvoted: bool | None = None


class Vote(VoteBase, SQLModel, table=True):
    __tablename__ = "votes"
    id: str = Field(primary_key=True, default_factory=nanoid.generate)
    user_id: str = Field(foreign_key="users.id")
    created_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
    )

    # Relationships
    user: User = Relationship(back_populates="votes")
    # Note: We could add a relationship to Chat and Message here if those models exist
    # chat: "Chat" = Relationship(back_populates="votes")
    # message: "Message" = Relationship(back_populates="votes")


class VoteOut(VoteBase):
    id: str
    user_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class VotesOut(CamelModel):
    data: list[VoteOut]
    count: int
