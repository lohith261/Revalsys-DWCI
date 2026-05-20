# Document + Web Chat Intelligence System

A premium, fullstack AI application that lets you upload PDF/DOCX documents, ask intelligent questions about them with perfect context retention, and seamlessly falls back to web search when documents don't contain the answer.

**Live Stack:** React frontend (Vercel) + FastAPI backend + Upstash Redis

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   React     │────▶│   FastAPI    │────▶│    ChromaDB     │
│  (Vercel)   │◄────│  (Render/    │◄────│  (Vector Store) │
│             │     │   Fly.io/    │     │                 │
│             │     │   Heroku)    │     │                 │
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

### 1. Configure Environment

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
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Step 2: Set Up Upstash Redis

**All backend platforms need a hosted Redis. Upstash is free and works everywhere.**

1. Go to [upstash.com](https://upstash.com) → **Create Database** → Redis
2. Copy the `REDIS_URL` (format: `redis://default:password@host:port`)
3. You'll paste this into your backend platform's environment variables

---

### Step 3: Choose & Deploy Backend

Pick **one** platform below. Render is the easiest free option.

#### Option A: Render (Recommended — Free Tier)

1. Go to [render.com](https://render.com) → sign in with GitHub
2. Click **New** → **Web Service** → Connect your GitHub repo
3. Configure:
   - **Name**: `document-web-chat-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`
4. Add environment variables:
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL` = `https://openrouter.ai/api/v1`
   - `LLM_MODEL` = `openai/gpt-4o-mini`
   - `REDIS_URL` = *(from Upstash)*
   - `CORS_ORIGINS` = `https://your-frontend.vercel.app` *(update after Vercel deploy)*
5. Click **Create Web Service**

**Note**: Free tier sleeps after 15 min inactivity. First request after sleep takes ~30s.

**Copy your backend URL** (e.g., `https://document-web-chat-backend.onrender.com`)

---

#### Option B: Fly.io (Generous Free Tier, Stays Awake)

1. Install Fly CLI:
   ```bash
   brew install flyctl  # macOS
   # or see https://fly.io/docs/hands-on/install-flyctl/
   ```
2. Login: `flyctl auth login`
3. Deploy backend:
   ```bash
   cd backend
   flyctl launch --name document-web-chat-backend --region iad --no-deploy
   flyctl secrets set OPENAI_API_KEY=sk-or-v1-...
   flyctl secrets set OPENAI_BASE_URL=https://openrouter.ai/api/v1
   flyctl secrets set LLM_MODEL=openai/gpt-4o-mini
   flyctl secrets set REDIS_URL=redis://... (from Upstash)
   flyctl secrets set CORS_ORIGINS=https://your-frontend.vercel.app
   flyctl deploy
   ```

**Copy your backend URL** (e.g., `https://document-web-chat-backend.fly.dev`)

**Note**: Fly.io free tier includes 3 shared-cpu-1m VMs. VMs stay awake.

---

#### Option C: Heroku (Simplest, But Paid)

1. Install Heroku CLI:
   ```bash
   brew install heroku  # macOS
   ```
2. Login: `heroku login`
3. Deploy:
   ```bash
   cd backend
   heroku create document-web-chat-backend
   heroku config:set OPENAI_API_KEY=sk-or-v1-...
   heroku config:set OPENAI_BASE_URL=https://openrouter.ai/api/v1
   heroku config:set LLM_MODEL=openai/gpt-4o-mini
   heroku config:set REDIS_URL=redis://... (from Upstash)
   heroku config:set CORS_ORIGINS=https://your-frontend.vercel.app
   git push heroku main
   ```

**Note**: Heroku has no free tier. Minimum $7/month for Eco dynos.

---

#### Option D: DigitalOcean App Platform ($5/month)

1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com) → **Create App**
2. Source: GitHub → select your repo
3. Source Directory: `backend/`
4. Environment: Python
5. Run Command: `gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`
6. Add environment variables (same as Render)
7. Deploy

---

#### Option E: PythonAnywhere (Free Tier)

1. Go to [pythonanywhere.com](https://pythonanywhere.com) → sign up
2. Open a Bash console
3. Clone your repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME/backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Go to **Web** tab → **Add a new web app** → **Manual configuration** → Python 3.11
5. Set WSGI file to use uvicorn:
   ```python
   import sys
   path = '/home/YOUR_USERNAME/YOUR_REPO_NAME/backend'
   if path not in sys.path:
       sys.path.append(path)
   from app.main import app
   application = app
   ```
6. Set environment variables in **WSGI configuration file** or via the web tab
7. Reload the web app

---

### Step 4: Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) → sign in with GitHub
2. Click **Add New Project** → Import your GitHub repo
3. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
4. Add environment variable:
   - `VITE_API_BASE` = `https://your-backend-url.com/api/v1`
     - Render example: `https://document-web-chat-backend.onrender.com/api/v1`
     - Fly.io example: `https://document-web-chat-backend.fly.dev/api/v1`
5. Click **Deploy**

**Copy your frontend URL** (e.g., `https://your-frontend.vercel.app`)

---

### Step 5: Connect Frontend ↔ Backend

After Vercel gives you a domain, update your backend's `CORS_ORIGINS`:

- **Render**: Go to dashboard → Environment → edit `CORS_ORIGINS` to `https://your-frontend.vercel.app`
- **Fly.io**: `flyctl secrets set CORS_ORIGINS=https://your-frontend.vercel.app && flyctl deploy`
- **Heroku**: `heroku config:set CORS_ORIGINS=https://your-frontend.vercel.app`
- **DigitalOcean**: Update in App Platform settings
- **PythonAnywhere**: Update in web tab environment variables

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
│   ├── Procfile           # Heroku / Render
│   ├── render.yaml        # Render
│   ├── fly.toml           # Fly.io
│   └── start.sh           # Startup script
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
