from functools import lru_cache

from app.services.vector_store import VectorStore
from app.services.redis_cache import RedisCache
from app.services.llm_client import LLMClient
from app.services.web_search import WebSearch
from app.services.chat_engine import ChatEngine
from app.services.document_processor import DocumentProcessor


@lru_cache()
def get_vector_store() -> VectorStore:
    return VectorStore()


@lru_cache()
def get_redis_cache() -> RedisCache:
    return RedisCache()


@lru_cache()
def get_llm_client() -> LLMClient:
    return LLMClient()


@lru_cache()
def get_web_search() -> WebSearch:
    return WebSearch()


@lru_cache()
def get_chat_engine() -> ChatEngine:
    return ChatEngine(
        get_vector_store(),
        get_redis_cache(),
        get_llm_client(),
        get_web_search(),
    )


@lru_cache()
def get_document_processor() -> DocumentProcessor:
    return DocumentProcessor()
