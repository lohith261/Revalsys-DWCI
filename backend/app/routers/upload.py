from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models.schemas import UploadResponse
from app.services.singletons import get_document_processor, get_vector_store, get_redis_cache

router = APIRouter(prefix="/api/v1")


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
        doc_processor = get_document_processor()
        vector_store = get_vector_store()
        redis_cache = get_redis_cache()

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
