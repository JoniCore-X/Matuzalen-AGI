from app.modules.ai.client import LLMClient
from app.modules.ai.schemas import AIPlanOutput


class AIPlannerService:
    def __init__(self, client: LLMClient | None = None):
        self.client = client or LLMClient()

    async def generate_plan(
        self,
        *,
        goal: str,
        hours_per_day: int,
        constraints: list[str],
    ) -> AIPlanOutput:
        system_prompt = '''Eres PlanBot, un planificador experto. Genera
      planes concretos y realistas. Responde solo JSON.'''
        user_prompt = f'''Genera un plan accionable en espanol para esta meta:
{goal}

Disponibilidad diaria: {hours_per_day} horas.
Restricciones: {', '.join(constraints) if constraints else 'ninguna'}.

Responde exclusivamente con JSON valido, sin Markdown, siguiendo este esquema:
{{
  "goal_title": "string",
  "summary": "string",
  "assumptions": ["string"],
  "missing_info": ["string"],
  "warnings": ["string"],
  "stages": [{{
    "title": "string",
    "description": "string",
    "position": 1,
    "tasks": [{{
      "title": "string",
      "description": "string",
      "priority": "high|medium|low",
      "estimated_minutes": 60,
      "depends_on": ["nombre de tarea"]
    }}]
  }}]
}}
Incluye de 2 a 5 etapas con tareas que quepan en la disponibilidad indicada.'''
        response = await self.client.call_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        return AIPlanOutput.model_validate(response)
