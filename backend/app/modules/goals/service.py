from typing import Any


class GoalService:
    def __init__(self, db):
        self.db = db

    def create_goal(self, *, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            'id': 'goal-1',
            'user_id': user_id,
            'title': payload['title'],
            'raw_input': payload['raw_input'],
            'description': payload.get('description'),
            'status': 'draft',
            'target_date': payload.get('target_date'),
            'hours_per_day': payload.get('hours_per_day', 2),
            'constraints': payload.get('constraints', []),
            'context': payload.get('context', {}),
            'progress_percentage': 0,
        }

    def list_goals(self, *, user_id: str) -> list[dict[str, Any]]:
        return [
            {
                'id': 'goal-1',
                'user_id': user_id,
                'title': 'Meta de ejemplo',
                'raw_input': 'Quiero lanzar un curso y organizar mi plan',
                'description': 'Meta inicial de prueba',
                'status': 'draft',
                'target_date': None,
                'hours_per_day': 2,
                'constraints': [],
                'context': {},
                'progress_percentage': 0,
            }
        ]
