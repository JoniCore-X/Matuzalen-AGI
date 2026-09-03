from app.dependencies import get_current_user
from app.modules.goals.schemas import GoalCreate, GoalOut, GoalUpdate
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix='/api/v1/goals', tags=['goals'])

GOALS_DB: dict[str, dict] = {}


@router.post('', response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, current_user=Depends(get_current_user)):
    goal_id = f'goal-{len(GOALS_DB) + 1}'
    goal = {
        'id': goal_id,
        'user_id': current_user['id'],
        'title': payload.title,
        'raw_input': payload.raw_input,
        'description': payload.description,
        'status': 'draft',
        'target_date': payload.target_date,
        'hours_per_day': payload.hours_per_day,
        'constraints': payload.constraints,
        'context': payload.context,
        'progress_percentage': 0,
    }
    GOALS_DB[goal_id] = goal
    return goal


@router.get('', response_model=list[GoalOut])
def list_goals(current_user=Depends(get_current_user)):
    return [goal for goal in GOALS_DB.values() if goal['user_id'] == current_user['id']]


@router.get('/{goal_id}', response_model=GoalOut)
def get_goal(goal_id: str, current_user=Depends(get_current_user)):
    goal = GOALS_DB.get(goal_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Goal not found')
    if goal['user_id'] != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')
    return goal


@router.patch('/{goal_id}', response_model=GoalOut)
def update_goal(goal_id: str, payload: GoalUpdate, current_user=Depends(get_current_user)):
    goal = GOALS_DB.get(goal_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Goal not found')
    if goal['user_id'] != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        goal[field] = value
    return goal
