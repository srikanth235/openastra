from datetime import datetime
from typing import TYPE_CHECKING

import nanoid
from sqlalchemy import DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .chat import Chat
    from .document import Document
    from .item import Item
    from .setting import Setting
    from .suggestion import Suggestion
    from .team import TeamMember
    from .tool_call import ToolCall
    from .vote import Vote


# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserRegister(SQLModel):
    email: str
    password: str
    full_name: str | None = None


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None
    updated_at: datetime = datetime.utcnow()


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None
    updated_at: datetime = datetime.utcnow()


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Database model, database table inferred from class name
class User(UserBase, table=True):
    __tablename__ = "users"
    id: str | None = Field(default_factory=nanoid.generate, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
    )
    items: list["Item"] = Relationship(back_populates="owner")
    settings: list["Setting"] = Relationship(
        cascade_delete=True, back_populates="owner"
    )
    tool_calls: list["ToolCall"] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    team_memberships: list["TeamMember"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    chats: list["Chat"] = Relationship(back_populates="user")
    votes: list["Vote"] = Relationship(back_populates="user", cascade_delete=True)
    documents: list["Document"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    suggestions: list["Suggestion"] = Relationship(
        back_populates="user", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserOut(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


class UsersOut(SQLModel):
    data: list[UserOut]
    count: int
