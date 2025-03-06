from datetime import datetime
from typing import TYPE_CHECKING

import nanoid
from sqlalchemy import Column, DateTime, func
from sqlmodel import JSON, Field, Relationship, SQLModel

from .base import CamelModel

if TYPE_CHECKING:
    from .chat import Chat


class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: str = Field(primary_key=True, default_factory=nanoid.generate)
    chat_id: str = Field(foreign_key="chats.id")
    role: str
    content: list | str | dict | None = Field(sa_column=Column(JSON))
    created_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )
    chat: "Chat" = Relationship(back_populates="messages")


class MessageCreate(CamelModel):
    role: str
    content: list | str | dict | None


class MessageOut(CamelModel):
    id: str
    chat_id: str
    role: str
    content: list | str | dict | None
    created_at: datetime | None = None


class MessagesOut(CamelModel):
    data: list[MessageOut]
    count: int
