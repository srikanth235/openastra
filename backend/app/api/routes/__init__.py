from fastapi import APIRouter

from app.api.routes import (
    chats,
    documents,
    execute,
    files,
    items,
    llm,
    login,
    projects,
    settings,
    suggestions,
    teams,
    users,
    utils,
    votes,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(
    suggestions.router, prefix="/suggestions", tags=["suggestions"]
)
api_router.include_router(votes.router, prefix="/votes", tags=["votes"])
api_router.include_router(execute.router, prefix="/execute", tags=["execute"])
