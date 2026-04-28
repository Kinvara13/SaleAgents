from fastapi import APIRouter

from app.api.v1.endpoints import projects, parsing, proposal_editor, chat, users, settings, auth, tenders, business_document, technical_document, proposal_plan, technical_case, pricing, review, pre_evaluation, health, tech_score, competitor_intel, bidding_game

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(business_document.router, prefix="/projects", tags=["business-documents"])
api_router.include_router(technical_document.router, prefix="/projects", tags=["technical-documents"])
api_router.include_router(technical_case.router, prefix="/projects", tags=["technical-cases"])
api_router.include_router(parsing.router, prefix="/parsing", tags=["parsing"])
api_router.include_router(proposal_editor.router, prefix="/proposal-editor", tags=["proposal-editor"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(tenders.router, prefix="/tenders", tags=["tenders"])
api_router.include_router(proposal_plan.router, prefix="/projects", tags=["proposal-plans"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["pricing"])
api_router.include_router(tech_score.router, prefix="/tech-score", tags=["tech-score"])
api_router.include_router(competitor_intel.router, prefix="/competitor-intel", tags=["competitor-intel"])
api_router.include_router(bidding_game.router, prefix="/bidding-game", tags=["bidding-game"])
api_router.include_router(review.router, prefix="/review", tags=["review"])
api_router.include_router(pre_evaluation.router, prefix="/pre-evaluation", tags=["pre-evaluation"])