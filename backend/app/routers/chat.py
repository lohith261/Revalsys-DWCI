from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse, SessionResponse, MessageItem, ReferencedFile
from app.services.singletons import get_chat_engine, get_redis_cache

router = APIRouter(prefix="/api/v1")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        chat_engine = get_chat_engine()
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
    redis_cache = get_redis_cache()
    messages = redis_cache.get_session_history(session_id)
    files = redis_cache.get_session_files(session_id)
    return SessionResponse(
        session_id=session_id,
        messages=[MessageItem(**m) for m in messages],
        files=files,
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    redis_cache = get_redis_cache()
    redis_cache.clear_session(session_id)
    return {"status": "deleted", "session_id": session_id}


@router.get("/sessions")
async def list_sessions():
    redis_cache = get_redis_cache()
    return redis_cache.get_all_sessions()
