from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse, SessionResponse, MessageItem, ReferencedFile
from app.services.chat_engine import ChatEngine
from app.services.vector_store import VectorStore
from app.services.redis_cache import RedisCache
from app.services.llm_client import LLMClient
from app.services.web_search import WebSearch

router = APIRouter(prefix="/api/v1")

# Shared service instances
vector_store = VectorStore()
redis_cache = RedisCache()
llm_client = LLMClient()
web_search = WebSearch()
chat_engine = ChatEngine(vector_store, redis_cache, llm_client, web_search)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = chat_engine.run(
            query=request.query,
            session_id=request.session_id,
            file_ids=request.file_ids,
        )
        return ChatResponse(
            answer=result["answer"],
            source=result["source"],
            session_id=result["session_id"],
            cached=result["cached"],
            referenced_files=[
                ReferencedFile(**f) for f in result["referenced_files"]
            ],
            generated_at=datetime.fromisoformat(result["generated_at"]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    messages = redis_cache.get_session_history(session_id)
    files = redis_cache.get_session_files(session_id)
    return SessionResponse(
        session_id=session_id,
        messages=[MessageItem(**m) for m in messages],
        files=files,
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    redis_cache.clear_session(session_id)
    return {"status": "deleted", "session_id": session_id}


@router.get("/sessions")
async def list_sessions():
    return redis_cache.get_all_sessions()
