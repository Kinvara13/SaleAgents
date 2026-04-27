# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SaleAgents is a bidding/intelligent agent MVP. The active codebase is in the `-v2` directories (`backend-v2/`, `frontend-v2/`). The legacy `backend/` and `frontend/` directories are inactive and described only in the root `README.md`.

- **Backend**: FastAPI + SQLAlchemy + SQLite (default) / PostgreSQL (production)
- **Frontend**: Vue 3 + Vite + Tailwind CSS + TypeScript
- **Default ports**: Backend 8000, Frontend 8081

## Common Commands

### Full-stack (development)
```bash
./start.sh          # Starts backend + frontend in dev mode (background, logs -> logs/)
./stop.sh           # Stops services started by start.sh
```

### Backend (`backend-v2/`)
```bash
cd backend-v2
source .venv/bin/activate

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Tests (pytest)
pytest                              # all tests
pytest tests/test_smoke.py -v       # specific file
pytest tests/test_smoke.py::test_health_check -v   # single test

# Database migrations (Alembic)
alembic upgrade head
alembic revision --autogenerate -m "description"

# Lint (ruff config in pyproject.toml)
ruff check .
```

### Frontend (`frontend-v2/`)
```bash
cd frontend-v2

# Dev server (port 8081, proxies /api -> localhost:8000)
npm run dev

# Build & preview
npm run build
npm run preview -- --host --port 8081

# Tests (vitest + jsdom)
npm run test                        # run once
npx vitest                          # watch mode
npx vitest run src/composables/__tests__/useLLMChat.spec.ts   # single file
```

## Architecture

### Backend

**Configuration**: Pydantic Settings reads from `.env` in the repository root. Key settings:
- `DATABASE_URL_OVERRIDE` — defaults to SQLite (`backend-v2/sale_agents_v2.db`); clear it to use PostgreSQL
- `FRONTEND_ORIGINS` — CORS allowlist (comma-separated)
- `LLM_*` — LLM provider configuration

**Layer responsibilities**:
- `endpoints/` — parameter validation, auth, response models, HTTP semantics
- `services/` — business logic, rule assembly, file processing, data aggregation
- `schemas/` — request/response contracts
- `models/` — database ORM models

**Important conventions**:
- The **single real API router entrypoint** is `backend-v2/app/api/router.py`. Any new endpoint must be explicitly imported and `include_router`-ed there.
- Auth is JWT Bearer token via `get_current_user` dependency. The test `conftest.py` overrides both `get_db` and `get_current_user` to use a test SQLite DB and a fake admin user.
- On startup (`app/main.py`), SQLAlchemy `create_all()` runs, demo tender data is seeded, and an APScheduler job is registered (30-minute interval tender fetch).
- Exported documents are served statically from `/exports` mounted at `backend-v2/exports/`.

### Frontend

**HTTP layer**: `src/services/api.ts` wraps axios with:
- Base URL from `VITE_API_BASE` + `/api/v1`
- Automatic Bearer token injection from `localStorage.sa_token`
- 401 refresh logic (calls `/auth/refresh`, falls back to `/login` on failure)
- Unified error logging

**Routing**: `src/router/index.ts` defines all routes. Layout-wrapped pages use `MainLayout.vue`. The router guard redirects unauthenticated users to `/login` (except routes with `meta: { public: true }`).

**Page state rule**: every page must handle `loading`, `empty`, `success`, and `error` states visibly.

## Development Rules (from `specs/`)

These are project-specific rules that are enforced in code review:

1. **Contract-first changes**: update `specs/api-contract-spec.md` before changing public API, then backend, then frontend.
2. **No business logic in endpoints**: keep endpoints thin; logic belongs in `services/`.
3. **Legacy compatibility**: old interfaces still used by the frontend must remain compatible and be marked `legacy` in `specs/api-contract-spec.md`.
4. **Database migrations**: do not rely on `Base.metadata.create_all()` for column-level changes. Provide explicit migration scripts or compatibility reads for schema drift.
5. **Axios is not fetch**: `api.ts` returns an axios response. Do **not** read `.ok` or call `.json()` on it. Use destructuring: `const { data } = await api.get('/users')`.
6. **Template strings for dynamic paths**: `` api.patch(`/users/${userId}`, payload) `` — never use un-interpolated strings with `$`.
7. **Documentation on completion**: after closing a feature, update `memory-bank/FEATURE_MATRIX_V2.md`, `TASK_BOARD_V2.md`, and `CHANGE_LOG_V2.md`.

## Testing

- **Backend**: `pytest` in `backend-v2/`. Smoke tests use `TestClient` with a test SQLite database and mocked auth.
- **Frontend**: `vitest` with `jsdom` environment and `@vue/test-utils`. Test files match `src/**/*.spec.ts`.
- **Default test credentials**: `admin / admin123`
