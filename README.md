# Data Log Visual

Web application for storing and visualizing automotive tuning datalogs, starting with COBB Access Port CSV exports.

## Current Status

- Backend foundation is implemented with FastAPI
- Frontend foundation is implemented with React + TypeScript + Vite
- Local Docker Compose workflow is included
- COBB CSV parsing, upload persistence, and initial visualization endpoints are in place

## Repository Layout

```text
backend/                 FastAPI API, auth, parser, persistence
frontend/                React + TypeScript UI
charts/data-log-visual/  Helm chart for frontend + backend deployment
data-logs/               Sample COBB export fixtures
planning/                Implementation planning docs
uploads/                 Local PVC-like upload directory for development
```

## Local Development

### Option 1: Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Frontend: [http://localhost:5173](http://localhost:5173)

Backend: [http://localhost:8000/api/healthz](http://localhost:8000/api/healthz)

### Option 2: Run Services Directly

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API Surface Today

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `PATCH /api/auth/me`
- `GET /api/healthz`
- `GET /api/uploads`
- `POST /api/uploads`
- `GET /api/uploads/{upload_id}`
- `GET /api/uploads/{upload_id}/visualization`
- `GET /api/uploads/{upload_id}/download`

## Notes

- Upload storage is PVC-backed filesystem storage for now.
- Alembic baseline migration is checked in under [backend/alembic/versions/20260418_0001_initial_schema.py](/Users/wardl/Personal/apps/data-log-visual/backend/alembic/versions/20260418_0001_initial_schema.py).
- Same-origin routing is expected in production: `/` for the frontend and `/api` for the backend on `datalog.lucas.engineering`.
- The implementation plan lives at [planning/mvp-implementation-plan.md](/Users/wardl/Personal/apps/data-log-visual/planning/mvp-implementation-plan.md).
