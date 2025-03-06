from typing import Any

import nanoid
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Chat,
    ChatOut,
    ChatsOut,
    ChatUpdate,
    Message,
)
from app.models.utils import UtilsMessage

router = APIRouter()


@router.get("/", response_model=ChatsOut)
def read_chats(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve chats. Optionally filter by project_id.
    """
    # Base query conditions
    conditions = [Chat.user_id == current_user.id]

    # Add project filter if provided
    if project_id:
        conditions.append(Chat.project_id == project_id)

    # Get count
    statement = select(func.count()).select_from(Chat).where(*conditions)
    count = session.exec(statement).one()

    # Get chats
    statement = (
        select(Chat)
        .where(*conditions)
        .order_by(Chat.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    chats = session.exec(statement).all()

    chat_out_list = [
        ChatOut(**chat.model_dump(exclude={"project"}), project=chat.project)
        for chat in chats
    ]
    return ChatsOut(data=chat_out_list, count=count)


@router.get("/{id}", response_model=ChatOut)
def read_chat(session: SessionDep, current_user: CurrentUser, id: str) -> ChatOut:
    """
    Get item by ID.
    """
    chat = session.get(Chat, id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if not current_user.is_superuser and (chat.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return ChatOut(**chat.model_dump(), project=chat.project)


@router.post("/", response_model=ChatOut)
def create_or_update_chat(
    *, session: SessionDep, current_user: CurrentUser, chat: Chat
) -> Any:
    """
    Create or update a chat.
    """
    # Get the existing chat, if any
    existing_chat: Chat = session.get(Chat, chat.id)

    # If the chat doesn't exist, create a new one
    if not existing_chat:
        # Set the user_id before validation to ensure it's included in the model
        chat_dict = chat.model_dump()
        chat_dict["user_id"] = str(current_user.id)
        chat = Chat.model_validate(chat_dict)
        session.add(chat)
        session.commit()
        session.refresh(chat)
        return ChatOut(**chat.model_dump(), project=chat.project)

    # Otherwise, update the existing chat
    if not current_user.is_superuser and (existing_chat.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = chat.model_dump(exclude_unset=True)
    existing_chat.sqlmodel_update(update_dict)
    session.add(existing_chat)
    session.commit()
    session.refresh(existing_chat)
    return ChatOut(**existing_chat.model_dump(), project=existing_chat.project)


@router.put("/{id}", response_model=ChatOut)
def update_chat(
    *, session: SessionDep, current_user: CurrentUser, id: str, chat_in: ChatUpdate
) -> Chat:
    """
    Update chat.
    """
    chat: Chat = session.get(Chat, id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if not current_user.is_superuser and (chat.user_id != str(current_user.id)):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_dict = chat_in.model_dump(exclude_unset=True)

    # Handle messages separately if they are provided
    messages = update_dict.pop("messages", None)

    # Update other fields
    chat.sqlmodel_update(update_dict)

    # Update messages if provided
    if messages is not None:
        # Delete existing messages
        for message in chat.messages:
            session.delete(message)

        # Add new messages
        if messages:
            # Convert dictionaries to Message objects
            message_objects = []
            for msg in messages:
                if isinstance(msg, dict):
                    msg_obj = Message(
                        id=msg.get("id", nanoid.generate()),
                        role=msg["role"],
                        content=msg["content"],
                        chat_id=chat.id,
                    )
                    message_objects.append(msg_obj)
                else:
                    # If it's already a Message object, just set the chat_id
                    msg.chat_id = chat.id
                    message_objects.append(msg)

            chat.messages = message_objects

    session.add(chat)
    session.commit()
    session.refresh(chat)
    return ChatOut(**chat.model_dump(), project=chat.project)


@router.delete("/{id}", response_model=UtilsMessage)
def delete_chat(session: SessionDep, current_user: CurrentUser, id: str) -> Any:
    """
    Delete chat.
    """
    chat: Chat = session.get(Chat, id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if not current_user.is_superuser and (chat.user_id != str(current_user.id)):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(chat)
    session.commit()
    return UtilsMessage(message="Chat deleted successfully")


@router.delete("/", response_model=UtilsMessage)
def delete_all_user_chats(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete all chats for a user.
    """
    session.query(Chat).filter(Chat.user_id == str(current_user.id)).delete()
    session.commit()
    return UtilsMessage(message="All chats deleted successfully")
