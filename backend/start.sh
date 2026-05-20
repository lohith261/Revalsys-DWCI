#!/bin/bash
set -e

echo "Starting Document Web Chat Backend..."

# Pre-download embedding model to avoid cold-start latency
python3 -c "
from sentence_transformers import SentenceTransformer
import os
model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
print(f'Downloading embedding model: {model_name}')
SentenceTransformer(model_name)
print('Embedding model ready.')
"

echo "Starting server..."
exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT:-8000} --timeout 120
