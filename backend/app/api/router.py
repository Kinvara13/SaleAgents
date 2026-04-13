from fastapi import APIRouter

from app.api.v1.endpoints import decision, documents, generation, health, llm_config, parsing, projects, review, system, workspace

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(parsing.router, prefix="/parsing", tags=["parsing"])
api_router.include_router(decision.router, prefix="/decision", tags=["decision"])
api_router.include_router(generation.router, prefix="/generation", tags=["generation"])
api_router.include_router(review.router, prefix="/review", tags=["review"])
api_router.include_router(llm_config.router, prefix="/llm-config", tags=["llm-config"])
