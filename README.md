# EDAMA — Elite:Dangerous Ask Me Anything

Elite Dangerous lore translation and knowledge system.
Translate Galnet articles from EN to CN, manage terminology
glossaries, and (coming soon) answer any question about the
Elite Dangerous universe through a RAG-powered chatbot.

## Modules

- **[Translator](backend/modules/translator/README.md)** —
  EN-CN article translation workflow with glossary,
  translation memory, and manual submission
- **Chatbot** (planned) — RAG-based Ask Me Anything
  for Elite Dangerous lore

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (App Router), React 19, Tailwind CSS 3, TypeScript |
| Backend | FastAPI, Python 3.11+ |
| API | REST / JSON |
| ORM | SQLAlchemy 2.x |
| Database | SQLite (development) |
| Migrations | Alembic |
| Scheduling | APScheduler |
| Linting | ruff, black |
| LLM Provider | openai (OpenAI SDK) |
| Vector Store | chromadb |
| Agent Framework | langgraph |

## Setup

```
git clone <repo-url>
cd Elite-Dangerous_Lore-Explainer-and-Translation-Project

# Backend
python -m venv .venv
source ./.venv/bin/activate    #Mac / Linux
.\.venv\Scripts\Activate.ps1  #Windows
pip install -e ".[dev]"
Copy-Item .env.example .env

# Frontend
cd frontend
npm install
```

Edit .env with your provider API keys, wiki credentials, and SMTP settings.

## Running

Start both services in separate terminals:

```
# Terminal 1 - frontend (port 3302)
cd frontend
npm run dev

# Terminal 2 - backend (port 3312)
uvicorn backend.main:app --port 3312
```

Open http://localhost:3302

Health check:

```
curl http://localhost:3312/health
```

## Development

```
# Apply database migrations
alembic upgrade head

# Create a migration after changing ORM models
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head

# Run tests
pytest

# Lint and format
ruff check .
black --check .
```

## Port Reference

| Service | Port |
|---------|------|
| Frontend (Next.js) | 3302 |
| Backend (FastAPI) | 3312 |
