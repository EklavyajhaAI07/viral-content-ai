# Viral AI: Your Content GEN

![Python](https://img.shields.io/badge/Python-56.4%25-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-38.2%25-3178c6)
![Next.js](https://img.shields.io/badge/Next.js-App%20Router-black)
![License](https://img.shields.io/badge/License-MIT-lightgrey)  
![Stars](https://img.shields.io/badge/Stars-0-informational)
![Forks](https://img.shields.io/badge/Forks-0-informational)

AI-powered “content studio” that scouts trends, designs strategy, generates content, and predicts virality—end-to-end.

---

## Problem Statement / Motivation

Creating consistently viral content is hard: you need trend awareness, platform-specific hooks, strong creative direction, and rapid iteration. This project packages that workflow into a single system with:
- an AI “crew” of specialized agents (trend scout, strategist, optimizer, predictor),
- a backend API with auth + job tracking,
- a Next.js UI for trends, strategy, and content creation.

---

## Features

- **Trend discovery** via a dedicated *Trend Scout* agent and trend tooling (`backend/app/tools/trend_engine.py`)
- **Content strategy generation** (`/strategy` route + strategist agent)
- **Content generation workflows** (`/generate`, `/content` routes)
- **Virality prediction/scoring** (virality predictor agent; UI gauge component)
- **Content optimization** (hooks, captions, hashtags, structure)
- **Thumbnail/image generation service** (`backend/app/services/thumbnail_service.py`)
- **Auth & session gating** (backend auth routes + frontend `SessionGate`)
- **Async/background tasks** (worker tasks module; Redis client present)
- **Database persistence + migrations** using Alembic  
  - migration includes **users** and **content_jobs** tables

---

## Tech Stack

### Backend
- **Python**
- **FastAPI** (API entrypoint: `backend/app/main.py`, routes under `backend/app/api/routes/`)
- **SQLAlchemy + Alembic** (migrations in `backend/alembic/`, config: `backend/alembic.ini`)
- **Redis** (client module: `backend/app/core/redis_client.py`)
- **LLM integration layer** (`backend/app/core/llm.py`)
- **Agent-based architecture** (`backend/app/agents/*`)
- **Pytest** (tests in `backend/tests/`)

### Frontend
- **Next.js (App Router)** (pages in `frontend/src/app/`)
- **TypeScript**
- **Tailwind CSS** (`frontend/tailwind.config.ts`, `frontend/src/app/globals.css`)
- **ESLint** (`frontend/.eslintrc.json`)

### Containerization
- **Docker** (frontend Dockerfile: `frontend/Dockerfile`)

---

## Project Structure

```text
.
├── backend
│   ├── README_SETUP.md
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 3e37938b2e68_create_users_and_content_jobs_tables.py
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/
│   │   │   ├── analyze.py
│   │   │   ├── auth.py
│   │   │   ├── content.py
│   │   │   ├── generate.py
│   │   │   ├── strategy.py
│   │   │   └── trends.py
│   │   ├── agents/
│   │   │   ├── algorithm_analyst.py
│   │   │   ├── content_optimizer.py
│   │   │   ├── strategist.py
│   │   │   ├── trend_scout.py
│   │   │   └── virality_predictor.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── llm.py
│   │   │   ├── redis_client.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── content.py
│   │   ├── schemas/
│   │   │   ├── requests.py
│   │   │   ├── user.py
│   │   │   └── content.py
│   │   ├── services/
│   │   │   ├── crew_service.py
│   │   │   ├── thumbnail_service.py
│   │   │   └── trend_service.py
│   │   ├── tools/
│   │   │   └── trend_engine.py
│   │   └── workers/
│   │       └── tasks.py
│   ├── outputs/                 # generated images (stability/pollinations)
│   ├── run_crew.py              # local crew runner
│   └── tests/                   # pytest suite
└── frontend
    ├── package.json
    ├── next.config.mjs
    ├── tailwind.config.ts
    └── src/
        ├── app/
        │   ├── page.tsx
        │   ├── login/page.tsx
        │   ├── trends/page.tsx
        │   ├── strategy/page.tsx
        │   └── content-studio/page.tsx
        ├── components/
        │   ├── Sidebar.tsx
        │   ├── SessionGate.tsx
        │   └── ScoreGauge.tsx
        └── lib/
            ├── api.ts
            └── demoData.ts
```

---

## Installation & Setup

> See `backend/README_SETUP.md` for backend-specific setup notes.

### 1) Backend (Python)

```bash
cd backend
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

#### Database migrations (Alembic)

```bash
cd backend
alembic upgrade head
```

> Configure DB connection and secrets in `backend/app/core/config.py` (environment-driven configuration is typically wired from here).

#### (Optional) Redis
If you use async/background flows, run Redis locally (example):

```bash
docker run -p 6379:6379 redis:alpine
```

### 2) Frontend (Next.js)

```bash
cd frontend
npm install
```

---

## Usage / Running the project

### Run Backend API

Common FastAPI run command (module entry: `backend/app/main.py`):

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API routes are organized under:

- `POST/GET` **Auth**: `backend/app/api/routes/auth.py`
- **Trends**: `backend/app/api/routes/trends.py`
- **Strategy**: `backend/app/api/routes/strategy.py`
- **Generate**: `backend/app/api/routes/generate.py`
- **Content**: `backend/app/api/routes/content.py`
- **Analyze**: `backend/app/api/routes/analyze.py`

### Run Frontend

```bash
cd frontend
npm run dev
```

Then open: `http://localhost:3000`

### Run the “Crew” locally (agent workflow)

```bash
cd backend
python run_crew.py
```

### Run tests

```bash
cd backend
pytest
```

---

## Screenshots

![WhatsApp Image 2026-04-04 at 2 34 52 PM](https://github.com/user-attachments/assets/fa079774-347a-437f-8879-bdc999553d7d)
![WhatsApp Image 2026-04-04 at 2 34 52 PM (1)](https://github.com/user-attachments/assets/ca8bddf2-21c9-41b5-bd4f-ad8412b54bf7)


---

## Demo

Coming soon.

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/my-change`
3. Commit: `git commit -m "Add my change"`
4. Push: `git push origin feat/my-change`
5. Open a Pull Request

Guidelines:
- Keep backend code modular under `backend/app/services/` and `backend/app/agents/`
- Add/extend Pydantic schemas in `backend/app/schemas/`
- Add tests under `backend/tests/` for new agent logic

---

## License

MIT (default).  
If you add a `LICENSE` file later, update this section to match its contents.
