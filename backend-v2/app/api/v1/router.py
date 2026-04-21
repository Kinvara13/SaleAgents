from fastapi import APIRouter

from app.api.v1.endpoints import projects, parsing, proposal_editor, chat, users, settings
from app.api.v1.endpoints import generation, workspace, decision, health, system

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(parsing.router, prefix="/parsing", tags=["parsing"])
api_router.include_router(proposal_editor.router, prefix="/proposal-editor", tags=["proposal-editor"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(generation.router, prefix="/generation", tags=["generation"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(decision.router, prefix="/decision", tags=["decision"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
