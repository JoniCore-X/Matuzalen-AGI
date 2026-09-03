import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from app.config.settings import get_settings
from app.core.exceptions import (AIGenerationError, AITimeoutError,
                                 AIValidationError)
from groq import APITimeoutError, AsyncGroq, GroqError

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, client: AsyncGroq | None = None):
        settings = get_settings()
        self.api_key = settings.groq_api_key or settings.llm_api_key
        self.model = settings.llm_model
        self.timeout = settings.llm_timeout / 1000
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
        self.client = client

    async def call_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 2,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise AIGenerationError('GROQ_API_KEY is not configured')

        client = self.client or AsyncGroq(
            api_key=self.api_key,
            timeout=self.timeout,
        )
        messages: list[dict[str, str]] = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ]
        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={'type': 'json_object'},
                )
                content = response.choices[0].message.content or ''
                payload = self._parse_json(content)
                usage = response.usage
                logger.info(
                    'llm_json_generation_succeeded model=%s input_tokens=%s '
                    'output_tokens=%s',
                    self.model,
                    getattr(usage, 'prompt_tokens', 0),
                    getattr(usage, 'completion_tokens', 0),
                )
                return payload
            except AIValidationError as exc:
                last_error = exc
                logger.warning(
                    'llm_json_generation_invalid attempt=%s model=%s',
                    attempt + 1,
                    self.model,
                )
                messages.extend([
                    {
                        'role': 'assistant',
                        'content': content if 'content' in locals() else '',
                    },
                    {
                        'role': 'user',
                        'content': (
                            'Devuelve solo JSON valido que respete el esquema '
                            'solicitado.'
                        ),
                    },
                ])
            except APITimeoutError as exc:
                raise AITimeoutError('The AI request timed out') from exc
            except GroqError as exc:
                raise AIGenerationError(
                    'The AI provider could not generate a plan'
                ) from exc

            if attempt < max_retries:
                await asyncio.sleep(0.25 * (attempt + 1))

        raise AIGenerationError(
            'The AI response remained invalid after retries'
        ) from last_error

    async def stream(
        self,
        *,
        messages: list[dict[str, str]],
    ) -> AsyncIterator[str]:
        if not self.api_key:
            raise AIGenerationError('GROQ_API_KEY is not configured')

        client = self.client or AsyncGroq(
            api_key=self.api_key,
            timeout=self.timeout,
        )
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            )
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except APITimeoutError as exc:
            raise AITimeoutError('The AI stream timed out') from exc
        except GroqError as exc:
            raise AIGenerationError(
                'The AI provider could not stream a response'
            ) from exc

    @staticmethod
    def estimate_cost(tokens_input: int, tokens_output: int) -> float:
        input_price_per_token = 0.20 / 1_000_000
        output_price_per_token = 0.20 / 1_000_000
        return (
            tokens_input * input_price_per_token
            + tokens_output * output_price_per_token
        )

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        cleaned = content.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned.split('\n', 1)[-1]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        try:
            payload = json.loads(cleaned.strip())
        except json.JSONDecodeError as exc:
            raise AIValidationError(
                'The AI response was not valid JSON'
            ) from exc
        if not isinstance(payload, dict):
            raise AIValidationError('The AI response must be a JSON object')
        return payload
