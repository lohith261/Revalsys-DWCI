from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import upload, chat
from app.services.vector_store import VectorStore
from app.services.redis_cache import RedisCache

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if not _origins or _origins == ["*"]:
    _origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(chat.router)

# Service health check instances
vector_store = VectorStore()
redis_cache = RedisCache()


@app.get("/api/v1/health")
async def health_check():
    from datetime import datetime
    redis_ok = redis_cache.health_check()
    # Simple vector db check
    vector_ok = True
    try:
        vector_store.collection.count()
    except Exception:
        vector_ok = False

    return {
        "status": "healthy" if (redis_ok and vector_ok) else "degraded",
        "redis": redis_ok,
        "vector_db": vector_ok,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    return {"message": "Document Web Chat Intelligence System", "version": "1.0.0"}
