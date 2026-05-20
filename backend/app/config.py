import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    openai_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "openai/gpt-4o-mini"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50
    similarity_threshold: float = 0.75
    cache_ttl: int = 3600
    session_ttl: int = 86400
    max_history_messages: int = 20
    app_name: str = "Document Web Chat Intelligence System"
    debug: bool = False
    cors_origins: str = "*"  # Comma-separated list, or "*" for all

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
