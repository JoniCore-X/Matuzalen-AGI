import httpx
from app.config.settings import get_settings

settings = get_settings()


class GroqClient:
    def __init__(self):
        self.api_key = settings.groq_api_key or settings.llm_api_key
        self.model = settings.llm_model
        self.base_url = 'https://api.groq.com/openai/v1'

    async def generate(self, prompt: str) -> dict:
        if not self.api_key:
            raise RuntimeError('GROQ_API_KEY is not configured')

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': settings.llm_temperature,
            'max_tokens': settings.llm_max_tokens,
        }

        timeout = settings.llm_timeout / 1000
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()
