from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default='PlanBot')
    env: str = Field(default='development')
    debug: bool = Field(default=True, validation_alias='APP_DEBUG')

    database_url: str = Field(
        default='postgresql+psycopg://postgres:postgres@'
        'db.your-project.supabase.co:5432/postgres'
    )
    supabase_url: str = Field(default='https://your-project.supabase.co')
    supabase_key: str = Field(default='')
    redis_url: str = Field(default='redis://localhost:6379/0')

    secret_key: str = Field(default='change-me-super-secret-key')
    algorithm: str = Field(default='HS256')
    access_token_expire_minutes: int = Field(default=60)

    llm_provider: str = Field(default='groq')
    llm_api_key: str = Field(default='')
    groq_api_key: str = Field(default='')
    llm_model: str = Field(default='qwen/qwen3.8-27b')
    llm_timeout: int = Field(default=30000)
    llm_max_tokens: int = Field(default=2000)
    llm_temperature: float = Field(default=0.4)

    default_timezone: str = Field(default='America/Mexico_City')
    django_settings_module: str = Field(default='django_project.settings')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
