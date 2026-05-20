# Document + Web Chat Intelligence System

A premium, fullstack AI application that lets you upload PDF/DOCX documents, ask intelligent questions about them with perfect context retention, and seamlessly falls back to web search when documents don't contain the answer.

**Live Stack:** React frontend (Vercel) + FastAPI backend (Railway/Render) + Upstash Redis

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   React     │────▶│   FastAPI    │────▶│    ChromaDB     │
│  (Vercel)   │◄────│  (Railway)   │◄────│  (Vector Store) │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Upstash     │
                    │  Redis       │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  DuckDuckGo  │
                    │  Web Search  │
                    └──────────────┘
```

---

## Features

- **Document Ingestion**: PDF and DOCX text extraction, cleaning, chunking, and embedding
- **Semantic Search**: Sentence-transformers embeddings with ChromaDB vector store
- **7-Step Query Pipeline**: Cache check → document retrieval → LLM generation → source labeling → cache storage
- **Web Search Fallback**: DuckDuckGo search when documents lack relevance
- **Session Management**: Full conversation history with Redis TTL (24h)
- **Smart Caching**: SHA-256 query hashing with 1-hour cache TTL
- **Premium UI**: Glassmorphism, Framer Motion animations, dark mode, drag-drop uploads

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 20+
- Redis (local or Upstash)
- OpenRouter API key

### 1. Clone & Configure

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Edit `.env` with your credentials:
```env
OPENAI_API_KEY=sk-or-v1-...
REDIS_URL=redis://localhost:6379/0
```

### 2. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

---

## Deployment Guide

### Step 1: Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/document-web-chat.git
git push -u origin main
```

### Step 2: Deploy Backend (Railway — Recommended)

1. Go to [Railway](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repo and the `backend` directory as the root
4. Add environment variables in Railway Dashboard:
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL` = `https://openrouter.ai/api/v1`
   - `LLM_MODEL` = `openai/gpt-4o-mini`
   - `REDIS_URL` = *(from Upstash, see below)*
   - `CORS_ORIGINS` = `https://your-frontend.vercel.app`
5. Railway auto-detects `requirements.txt` and `Procfile`
6. Copy your backend URL (e.g., `https://document-web-chat-backend.up.railway.app`)

**Alternative: Render**
1. Go to [Render](https://render.com) → **New Web Service**
2. Connect your GitHub repo
3. Set root directory to `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`
6. Add environment variables同上

### Step 3: Set Up Upstash Redis

1. Go to [Upstash](https://upstash.com) → **Create Database**
2. Choose the Redis option
3. Copy the `REDIS_URL` (format: `redis://default:password@host:port`)
4. Paste it into your backend environment variables

### Step 4: Deploy Frontend (Vercel)

1. Go to [Vercel](https://vercel.com) and sign in with GitHub
2. Click **Add New Project** → Import your GitHub repo
3. Set **Framework Preset** to `Vite`
4. Set **Root Directory** to `frontend`
5. Add environment variable:
   - `VITE_API_BASE` = `https://your-backend.railway.app/api/v1`
6. Click **Deploy**

### Step 5: Connect Frontend ↔ Backend

1. Update backend `CORS_ORIGINS` env var with your Vercel domain:
   ```
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
2. Redeploy backend if you changed CORS settings

---

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `OPENAI_API_KEY` | — | OpenRouter / OpenAI API key |
| `OPENAI_BASE_URL` | `https://openrouter.ai/api/v1` | API endpoint base URL |
| `LLM_MODEL` | `openai/gpt-4o-mini` | LLM model name |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Local embedding model |
| `CHUNK_SIZE` | `500` | Text chunk size (words) |
| `CHUNK_OVERLAP` | `50` | Chunk overlap (words) |
| `SIMILARITY_THRESHOLD` | `0.75` | Min similarity for document match |
| `CACHE_TTL` | `3600` | Response cache TTL (seconds) |
| `SESSION_TTL` | `86400` | Session history TTL (seconds) |
| `MAX_HISTORY_MESSAGES` | `20` | Max messages per session |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE` | `http://localhost:8000/api/v1` | Backend API base URL |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload` | Upload PDF/DOCX file |
| POST | `/api/v1/chat` | Send a chat query |
| GET | `/api/v1/session/{id}` | Get session history |
| DELETE | `/api/v1/session/{id}` | Clear session |
| GET | `/api/v1/sessions` | List all sessions |
| GET | `/api/v1/health` | Health check |

---

## Testing

```bash
# Start local backend first
uvicorn app.main:app --port 8000

# Run test flow
cd backend
python tests/test_flow.py
```

The test script:
1. Creates a sample DOCX file
2. Uploads it
3. Asks 2 document questions
4. Verifies cache hit on repeat question
5. Tests web fallback with an off-topic query
6. Verifies session history
7. Cleans up session

---

## Tech Stack

**Backend:**
- FastAPI + Uvicorn + Gunicorn
- ChromaDB (vector store)
- sentence-transformers (embeddings)
- Redis (cache + sessions)
- OpenRouter API (LLM)
- duckduckgo-search (web fallback)
- pdfplumber + python-docx (parsing)

**Frontend:**
- React 18 + TypeScript
- TailwindCSS
- Framer Motion
- React Query
- react-markdown
- Lucide React
- date-fns

---

## Project Structure

```
document-web-chat/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/schemas.py
│   │   ├── services/
│   │   │   ├── document_processor.py
│   │   │   ├── vector_store.py
│   │   │   ├── chat_engine.py
│   │   │   ├── web_search.py
│   │   │   ├── redis_cache.py
│   │   │   └── llm_client.py
│   │   ├── routers/
│   │   │   ├── upload.py
│   │   │   └── chat.py
│   │   └── utils/text_cleaner.py
│   ├── tests/test_flow.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── railway.json
│   ├── render.yaml
│   └── start.sh
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── SourceBadge.tsx
│   │   │   ├── FileUploader.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TypingIndicator.tsx
│   │   │   └── PromptSuggestions.tsx
│   │   ├── hooks/
│   │   │   ├── useChat.ts
│   │   │   └── useUpload.ts
│   │   ├── services/api.ts
│   │   └── types/index.ts
│   ├── package.json
│   ├── vercel.json
│   └── .env.example
├── .env.example
├── .gitignore
└── README.md
```

---

## License

MIT
