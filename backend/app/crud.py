from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Chat,
    Item,
    ItemCreate,
    Project,
    ProjectCreate,
    Setting,
    SettingCreate,
    Team,
    TeamCreate,
    TeamInvitationStatus,
    TeamMember,
    TeamRole,
    User,
    UserCreate,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    create_setting(session=session, setting_create=SettingCreate(), owner_id=db_obj.id)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: int) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_chat(*, session: Session, chat: Chat) -> Chat:
    db_chat = Chat.model_validate(chat.model_dump())
    session.add(db_chat)
    session.commit()
    session.refresh(db_chat)
    return db_chat


def create_setting(
    *, session: Session, setting_create: SettingCreate, owner_id: str
) -> Setting:
    db_setting = Setting.model_validate(setting_create, update={"owner_id": owner_id})
    session.add(db_setting)
    session.commit()
    session.refresh(db_setting)
    return db_setting


def create_team(*, session: Session, team_create: TeamCreate, owner_id: str) -> Team:
    team = Team.model_validate(team_create)
    session.add(team)
    session.commit()
    session.refresh(team)
    # Create a TeamMember entry for the owner
    team_member = TeamMember(
        team_id=team.id,
        user_id=owner_id,
        role=TeamRole.OWNER,
        invitation_status=TeamInvitationStatus.ACCEPTED,
    )
    session.add(team_member)
    session.commit()
    session.refresh(team)
    return team


def get_chats(session: Session, user_id: str) -> list[Chat]:
    statement = select(Chat).where(Chat.user_id == user_id)
    return session.exec(statement).all()


def create_project(*, session: Session, project_create: ProjectCreate) -> Project:
    db_project = Project.model_validate(project_create)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project
