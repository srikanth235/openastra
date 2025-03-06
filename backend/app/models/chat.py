from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, ForwardRef

import nanoid
from sqlalchemy import DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from .base import CamelModel
from .message import Message
from .project import Project
from .user import User

if TYPE_CHECKING:
    from .message import Message


class ChatBase(CamelModel):
    title: str | None = None
    path: str | None = None


class ChatVisibility(str, Enum):
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"


class Chat(ChatBase, SQLModel, table=True):
    __tablename__ = "chats"
    id: str = Field(primary_key=True, default_factory=nanoid.generate)
    user_id: str = Field(foreign_key="users.id")
    project_id: str | None = Field(default=None, foreign_key="projects.id")
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
    visibility: ChatVisibility = Field(default=ChatVisibility.PRIVATE)

    # Relationships
    user: User = Relationship(back_populates="chats")
    project: Project | None = Relationship(back_populates="chats")
    messages: list["Message"] = Relationship(back_populates="chat")


class ChatUpdate(CamelModel):
    title: str | None = None
    project_id: str | None = None
    updated_at: datetime = datetime.utcnow()
    messages: list[ForwardRef("Message")] | None = None


class ChatOut(ChatBase):
    id: str
    user_id: str
    visibility: ChatVisibility
    project_id: str | None = None
    project: Project | None = None
    messages: list[ForwardRef("Message")] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "abc123",
                    "title": "Sample Chat",
                    "path": "sample-path",
                    "user_id": "user123",
                    "visibility": "private",
                    "project_id": None,
                    "messages": [],
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                }
            ]
        }
    }


class ChatsOut(CamelModel):
    data: list[ChatOut]
    count: int


# Update forward references
ChatOut.model_rebuild()
