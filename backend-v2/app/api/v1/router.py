from fastapi import APIRouter

from app.api.v1.endpoints import projects, parsing, proposal_editor, chat, users, settings

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(parsing.router, prefix="/parsing", tags=["parsing"])
api_router.include_router(proposal_editor.router, prefix="/proposal-editor", tags=["proposal-editor"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
