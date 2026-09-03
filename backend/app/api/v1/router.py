from app.modules.ai.router import router as ai_router
from app.modules.auth.router import router as auth_router
from app.modules.goals.router import router as goals_router
from fastapi import APIRouter

router = APIRouter(prefix='/api/v1')
router.include_router(auth_router)
router.include_router(goals_router)
router.include_router(ai_router)
