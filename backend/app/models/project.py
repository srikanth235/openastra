from datetime import datetime
from typing import Any

import nanoid
from sqlalchemy import Column, DateTime, func
from sqlmodel import JSON, Field, Relationship, SQLModel

from .base import CamelModel
from .team import Team


class ProjectBase(CamelModel):
    title: str
    description: str | None = None
    model: str | None = None
    instructions: str | None = None


class ProjectCreate(ProjectBase):
    team_id: str | None = None


class ProjectUpdate(CamelModel):
    title: str | None = None
    description: str | None = None
    model: str | None = None
    instructions: str | None = None
    files: list[str] | None = None
    new_files: Any | None = None
    # updated_at: datetime = datetime.utcnow()


class Project(ProjectBase, SQLModel, table=True):
    __tablename__ = "projects"
    id: str = Field(default_factory=nanoid.generate, primary_key=True)
    files: list[str] | None = Field(default=[], sa_column=Column(JSON))

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
    team_id: str = Field(foreign_key="teams.id", nullable=False)
    team: Team = Relationship(back_populates="projects")
    chats: list["Chat"] = Relationship(back_populates="project")  # noqa: F821
    documents: list["Document"] = Relationship(back_populates="project")  # noqa: F821


class ProjectOut(ProjectBase):
    id: str
    team_id: str
    files: list[str] | None = []
    created_at: datetime
    updated_at: datetime


class ProjectsOut(CamelModel):
    data: list[ProjectOut]
    count: int
