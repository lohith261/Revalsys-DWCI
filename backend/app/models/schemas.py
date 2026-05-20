from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    session_id: Optional[str] = None


class UploadResponse(BaseModel):
    file_id: str
    file_name: str
    chunks_indexed: int
    status: str
    timestamp: datetime


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    session_id: str
    file_ids: Optional[List[str]] = None


class ReferencedFile(BaseModel):
    file_id: str
    file_name: str
    relevance_score: float


class ChatResponse(BaseModel):
    answer: str
    source: str = Field(..., pattern="^(document|web)$")
    session_id: str
    cached: bool
    referenced_files: List[ReferencedFile]
    generated_at: datetime


class MessageItem(BaseModel):
    role: str
    content: str
    source: Optional[str] = None
    timestamp: datetime


class SessionResponse(BaseModel):
    session_id: str
    messages: List[MessageItem]
    files: List[dict]


class HealthResponse(BaseModel):
    status: str
    redis: bool
    vector_db: bool
    timestamp: datetime
