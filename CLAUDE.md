# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

AI Coding 运营看板 — a single-page operations dashboard for AI Coding usage, token cost, and MR merge metrics. It has a Python FastAPI backend and a React + TypeScript frontend. The backend currently serves mock data; a PostgreSQL + SQLAlchemy ORM layer is in place for real lake-table / CodeHub integrations.

## Common commands

### Backend

Run from `backend/` with Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health check: `GET http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

There is currently no test runner, lint command, or formatter configured for the backend.

### Frontend

Run from `frontend/` (uses pnpm):

```bash
pnpm install
pnpm dev
```

Build for production (`tsc -b && vite build`, output to `frontend/dist`):

```bash
pnpm build
```

There is currently no test runner, lint command, or formatter configured for the frontend.

## Architecture

### Data flow

`App.tsx` (state) → `api.ts` (fetch) → FastAPI routes (`routes.py`) → `DashboardDataProvider` (abstract) → `MockDashboardDataProvider` (concrete).

The dashboard loads in two sequential calls: `getFilterOptions()` to populate filter dropdowns, then `getOverview(filters)` to fetch all KPI/chart/table data. Subsequent filter changes re-call `getOverview`.

### Backend

- `backend/app/main.py` — FastAPI application factory (`create_app`). Configures CORS and mounts the dashboard router under `settings.api_prefix` (`/api`).
- `backend/app/core/config.py` — Pydantic-settings based config, read from `backend/.env` with `AICODING_` prefix.
- `backend/app/api/routes.py` — Dashboard API routes under `/api/dashboard`. All endpoints receive a `DashboardDataProvider` via `Depends(get_data_provider)`.
- `backend/app/dependencies.py` — Factory that selects the data provider based on `AICODING_DATA_PROVIDER`. Supported values: `mock` (in-memory mock data), `sql` (SQLAlchemy-backed, currently delegates to mock). This is the only file to edit when wiring in a new provider.
- `backend/app/services/provider.py` — `DashboardDataProvider` abstract base class defining 11 methods. New real-world providers should subclass this without changing routes or schemas.
- `backend/app/services/mock_provider.py` — `MockDashboardDataProvider`, in-memory mock implementation.
- `backend/app/services/sql_provider.py` — `SqlDashboardDataProvider`, skeleton that delegates all 11 methods to mock. Replace individual methods with real SQLAlchemy queries as data sources become available.
- `backend/app/schemas.py` — Pydantic request/response models shared with the frontend types. **Keep these in sync with `frontend/src/types.ts`.**
- `backend/app/models/` — SQLAlchemy 2.0 ORM models (declarative, async). 9 tables: `pdu`, `lm_team`, `user` (dimension tables), `ai_model`, `repository` (reference tables), `token_usage`, `merge_request`, `tool_call`, `user_issue` (fact/event tables). ORM models are separate from API schemas — the former describe database structure, the latter describe API contracts.
- `backend/app/db/` — Async database session management. `session.py` provides lazy-singleton `AsyncEngine`, `async_sessionmaker`, and `get_db()` FastAPI dependency.
- `backend/alembic/` — Alembic migrations directory. `env.py` reads database URL from app config, supports async engine for online migrations.

Key API contracts:

- `GET /api/dashboard/filters` returns filter option lists.
- `POST /api/dashboard/overview` returns KPIs, trends, rankings, quadrant, insights, and detail tables.
- `POST /api/dashboard/users`, `/mrs`, `/tokens` return detail tables.
- `POST /api/dashboard/reports/export` returns a mocked export job response.

To replace mock data with a real provider: subclass `DashboardDataProvider`, import it in `dependencies.py`, and map the desired `AICODING_DATA_PROVIDER` value to it. Planned real sources: CodeAgent GUI/CLI lake tables (users, sessions, prompts, tokens, tool calls), CodeHub MR data (AI-generated lines, total lines, repository, author), and an org mapping table (`user_id → PDU → LM team`).

### Database & Migrations

This project uses **PostgreSQL + SQLAlchemy 2.0 (async) + Alembic**. ORM models (`backend/app/models/`) are strictly separate from API schemas (`backend/app/schemas.py`) — they serve different purposes and evolve independently.

**Data provider modes:**

| `AICODING_DATA_PROVIDER` | Implementation | Requires PostgreSQL |
|---|---|---|
| `mock` (default) | `MockDashboardDataProvider` — in-memory data | No |
| `sql` | `SqlDashboardDataProvider` — currently delegates to mock | No (yet) |

The `sql` provider is a gradual-migration skeleton: it implements the full ABC but delegates every method to mock. Replace methods one by one with real SQLAlchemy queries when the corresponding data source is ready.

**Database setup (for when a real DB is connected):**

```bash
# 1. Ensure PostgreSQL is running and create the database
createdb aicoding

# 2. Set the connection string in backend/.env
# AICODING_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aicoding

# 3. Run migrations
cd backend
source .venv/bin/activate
alembic upgrade head

# 4. Start with sql provider
AICODING_DATA_PROVIDER=sql uvicorn app.main:app --reload
```

**Migration workflow (day-to-day development):**

```bash
# After editing ORM models, generate a new migration:
alembic revision --autogenerate -m "describe your change"

# Review the generated file in alembic/versions/, then apply:
alembic upgrade head

# Roll back one migration:
alembic downgrade -1

# Check current migration state:
alembic current

# Generate SQL without executing (dry-run):
alembic upgrade head --sql
```

**Key design decisions:**

- **Async engine**: `create_async_engine` with `asyncpg` driver. `pool_pre_ping=True` prevents stale connections.
- **Lazy singleton**: Engine and session factory are created on first use, so models can be imported without a running database.
- **`expire_on_commit=False`**: Prevents detached-instance errors after session commit.
- **Alembic env.py**: Reads `database_url` from `app.core.config` (not hardcoded in `alembic.ini`). Uses `connection.run_sync()` for async-compatible migrations.
- **Initial migration**: `9f643031f6bb` creates all 9 tables with indexes and foreign keys. It can be applied once a real PostgreSQL instance is available.
- **No downgrade safety net**: Downgrades are defined but untested — review the generated SQL before running `downgrade` in production.

### Frontend

- `frontend/src/App.tsx` — Shell: sidebar navigation, `activePage` state, renders `OverviewPage` or `CodeMergePage`. Add new pages here.
- `frontend/src/pages/OverviewPage.tsx` — Entire overview dashboard: filter bar, KPI cards, ECharts charts, ranking table, insights, detail tabs.
- `frontend/src/pages/CodeMergePage.tsx` — Code merge analysis page: 5 KPI cards, PDU stacked bar, trend line, repo Top 10, contributor scatter, paginated/sortable MR table.
- `frontend/src/api.ts` — Thin fetch wrapper. Reads `VITE_API_BASE_URL` (defaults to `/api`). Exports `getFilterOptions`, `getOverview`, `exportReport`, `getCodeMergeOverview`, `getCodeMergeMrs`, and default filter objects.
- `frontend/src/types.ts` — TypeScript interfaces that mirror `backend/app/schemas.py`. **Keep these in sync when changing API contracts.**
- `frontend/src/styles.css` — All component styling; no CSS framework is used.
- `frontend/vite.config.ts` — Vite + React plugin; proxies `/api` to `http://127.0.0.1:8000` during development.

## Environment variables

- `backend/.env` (copy from `backend/.env.example`):
  - `AICODING_DATA_PROVIDER=mock` — or `sql` for SQLAlchemy-backed provider
  - `AICODING_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]`
  - `AICODING_DATABASE_URL=postgresql+asyncpg://aicoding:aicoding@localhost:5432/aicoding`
- `frontend/.env` (copy from `frontend/.env.example`):
  - `VITE_API_BASE_URL=/api`

## Production deployment

Build the frontend (`frontend/dist`) and serve it via Nginx or a static host. Reverse-proxy `/api` to the FastAPI backend. Set `AICODING_CORS_ORIGINS` to the real frontend origin and `AICODING_DATA_PROVIDER` to the real provider name. Backend production start:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
