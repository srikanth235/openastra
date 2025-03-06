from datetime import datetime

import nanoid
from sqlalchemy import DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from .base import CamelModel
from .document import Document
from .user import User


class SuggestionBase(CamelModel):
    document_id: str = Field(foreign_key="documents.id")
    original_text: str
    suggested_text: str
    description: str | None = None
    is_resolved: bool = False


class SuggestionCreate(SuggestionBase):
    pass


class SuggestionUpdate(CamelModel):
    suggested_text: str | None = None
    description: str | None = None
    is_resolved: bool | None = None


class Suggestion(SuggestionBase, SQLModel, table=True):
    __tablename__ = "suggestions"
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
    user: User = Relationship(back_populates="suggestions")
    document: Document = Relationship(back_populates="suggestions")


class SuggestionOut(SuggestionBase):
    id: str
    user_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SuggestionsOut(CamelModel):
    data: list[SuggestionOut]
    count: int
