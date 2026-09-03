from app.core.exceptions import AIGenerationError, AITimeoutError
from app.dependencies import get_current_user
from app.modules.ai.schemas import PlanGenerationRequest
from app.modules.ai.service import AIPlannerService
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix='/plans', tags=['ai'])
planner_service = AIPlannerService()


@router.post('/generate')
async def generate_plan(
    payload: PlanGenerationRequest,
    current_user=Depends(get_current_user),
):
    try:
        plan = await planner_service.generate_plan(
            goal=payload.goal,
            hours_per_day=payload.hours_per_day,
            constraints=payload.constraints,
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail='Groq returned an invalid plan response',
        ) from exc
    except AITimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail='The AI request timed out. Try again shortly.',
        ) from exc
    except AIGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return {'user_id': current_user['id'], 'plan': plan}
