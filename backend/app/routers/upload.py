from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models.schemas import UploadResponse
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.services.redis_cache import RedisCache

router = APIRouter(prefix="/api/v1")

# Shared service instances
doc_processor = DocumentProcessor()
vector_store = VectorStore()
redis_cache = RedisCache()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.lower().split(".")[-1]
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Only .pdf and .docx files are supported")

    try:
        contents = await file.read()
        file_id, cleaned_text, chunks = doc_processor.process_file(contents, file.filename)
        chunks_indexed = vector_store.index_chunks(file_id, file.filename, chunks)

        if session_id:
            redis_cache.add_session_file(session_id, {
                "file_id": file_id,
                "file_name": file.filename,
                "uploaded_at": datetime.utcnow().isoformat(),
                "chunks_indexed": chunks_indexed,
            })

        return UploadResponse(
            file_id=file_id,
            file_name=file.filename,
            chunks_indexed=chunks_indexed,
            status="processed",
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
