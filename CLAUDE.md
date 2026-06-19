# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

AI Coding 运营看板 — a single-page operations dashboard for AI Coding usage, token cost, and MR merge metrics. It has a Python FastAPI backend and a React + TypeScript frontend. The backend currently serves mock data only; real lake-table / CodeHub integrations are planned.

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
- `backend/app/dependencies.py` — Factory that selects the data provider based on `AICODING_DATA_PROVIDER`. Currently only `mock` is supported; this is the only file to edit when wiring in a new provider.
- `backend/app/services/provider.py` — `DashboardDataProvider` abstract base class. New real-world providers should subclass this without changing routes or schemas.
- `backend/app/services/mock_provider.py` — `MockDashboardDataProvider`, the only implementation right now.
- `backend/app/schemas.py` — Pydantic request/response models shared with the frontend types.

Key API contracts:

- `GET /api/dashboard/filters` returns filter option lists.
- `POST /api/dashboard/overview` returns KPIs, trends, rankings, quadrant, insights, and detail tables.
- `POST /api/dashboard/users`, `/mrs`, `/tokens` return detail tables.
- `POST /api/dashboard/reports/export` returns a mocked export job response.

To replace mock data with a real provider: subclass `DashboardDataProvider`, import it in `dependencies.py`, and map the desired `AICODING_DATA_PROVIDER` value to it. Planned real sources: CodeAgent GUI/CLI lake tables (users, sessions, prompts, tokens, tool calls), CodeHub MR data (AI-generated lines, total lines, repository, author), and an org mapping table (`user_id → PDU → LM team`).

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
  - `AICODING_DATA_PROVIDER=mock`
  - `AICODING_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]`
- `frontend/.env` (copy from `frontend/.env.example`):
  - `VITE_API_BASE_URL=/api`

## Production deployment

Build the frontend (`frontend/dist`) and serve it via Nginx or a static host. Reverse-proxy `/api` to the FastAPI backend. Set `AICODING_CORS_ORIGINS` to the real frontend origin and `AICODING_DATA_PROVIDER` to the real provider name. Backend production start:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
