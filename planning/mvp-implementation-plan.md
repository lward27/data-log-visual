# Data Log Visual MVP Implementation Plan

## Product Goal

Build a web app for automotive tuning datalogs, starting with COBB Access Port CSV exports. Users should be able to create an account, upload datalogs, return later to view their history, and visualize the metrics contained in each log.

## Locked Decisions

- Repository home: `apps/data-log-visual`
- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLModel + Alembic + PostgreSQL
- Auth: email/password with secure `HttpOnly` cookie auth
- Storage: PostgreSQL for application data, PVC-backed filesystem storage for original uploaded CSVs
- Deployment: single repo, separate frontend and backend images, one Helm chart, deployed into `apps-prod`
- Ingress strategy: single public hostname with same-origin API routing
  - `https://datalog.lucas.engineering/` -> frontend
  - `https://datalog.lucas.engineering/api/...` -> backend

## MVP Scope

### In Scope

- User signup, login, logout, and profile retrieval
- Upload COBB datalog CSV files
- Retain the original uploaded CSV
- Parse and normalize the uploaded data
- Persist parsed log metadata and chart-friendly metric series
- Browse previously uploaded logs
- View a log detail page with interactive metric visualization

### Out of Scope for MVP

- Password reset
- Social login
- Garage / multi-car management
- Cross-log comparison
- Non-COBB tuner formats
- Object storage

## Architectural Direction

### Repository Layout

```text
apps/data-log-visual/
  backend/
  frontend/
  charts/data-log-visual/
  data-logs/
  planning/
  docker-compose.yml
  README.md
```

### Frontend

- React + TypeScript + Vite SPA
- Same-origin API access through `/api`
- Charting library optimized for large synchronized time series
- Pages:
  - auth
  - upload
  - log library
  - log detail / visualization

### Backend

- FastAPI application with modular routers and services
- SQLModel for models and database access
- Alembic migrations
- Session-based auth using secure `HttpOnly` cookies
- Parser service for COBB CSV ingestion and normalization

### Data Storage

- PostgreSQL stores:
  - users
  - auth sessions
  - datalog uploads
  - metric definitions / availability
  - parsed time-series payloads
  - upload summaries
- PVC-backed upload directory stores original CSV files

### Parsing Strategy

- Treat COBB CSV as the initial supported format
- Support `latin-1` / Windows-style encodings when reading uploads
- Normalize headers into:
  - display name
  - slug / stable metric key
  - unit
- Extract metadata from the `AP Info` column header
- Preserve the original column names alongside normalized forms

## Delivery Plan

## Wave 0: Architecture and Contracts

### Phase 0.1: Monorepo Structure

- Create `backend`, `frontend`, and `charts/data-log-visual`
- Add local development conventions and root documentation

### Phase 0.2: Ingress and Auth Contract

- Use same-host `/api` routing
- Use secure cookie auth to avoid token handling in the browser

### Phase 0.3: Parser Contract

- Define file validation rules
- Define encoding fallback behavior
- Define metric normalization rules
- Define extracted upload metadata contract

### Phase 0.4: Persistence Model

- Define database schema for users, sessions, uploads, summaries, and metric series
- Store chart-ready data per upload and metric

## Wave 1: Foundation and Local Developer Experience

### Phase 1.1: Backend Scaffold

- FastAPI app
- config management
- database setup
- models
- migrations
- tests
- health endpoints

### Phase 1.2: Frontend Scaffold

- React + TypeScript + Vite app
- routing
- auth screens
- upload page shell
- library page shell
- visualization page shell

### Phase 1.3: Local Tooling

- `docker-compose.yml` for frontend, backend, and postgres
- `.env.example` files
- scripts / Make targets for common workflows

## Wave 2: Auth and Account Flow

### Phase 2.1: Backend Auth

- signup endpoint
- login endpoint
- logout endpoint
- current-user endpoint

### Phase 2.2: Frontend Auth

- signup form
- login form
- protected routes
- persisted login state

### Phase 2.3: Profile

- minimal current-user profile page

## Wave 3: Datalog Ingestion

### Phase 3.1: Upload API

- file type and size validation
- secure user ownership checks
- original file persistence

### Phase 3.2: Parser Implementation

- load COBB CSV
- normalize columns
- extract summaries
- produce chart-ready series data

### Phase 3.3: Upload Persistence

- store upload metadata
- store metric availability
- store metric series

## Wave 4: Visualization MVP

### Phase 4.1: Log Library

- list uploads by user
- sort and filter basics

### Phase 4.2: Log Detail

- metric picker
- synchronized timeseries charts
- hover tooltip, zoom, reset

### Phase 4.3: Summary Cards

- duration
- sample count
- min / max for key metrics
- tune / device metadata

## Wave 5: Deployment and Cluster Integration

### Phase 5.1: Containers

- backend Dockerfile
- frontend Dockerfile

### Phase 5.2: Helm

- one chart that deploys:
  - frontend deployment/service
  - backend deployment/service
  - ingress
  - secrets / config wiring
  - PVC-backed upload storage

### Phase 5.3: Cluster Registration

- add root-app registration in `lucas_engineering`
- deploy into `apps-prod`

### Phase 5.4: Tekton Support

- extend `tekton-ci` to support multiple services from one repo with different `dockerfile` and `context` values

## Wave 6: Testing and Hardening

### Phase 6.1: Backend Tests

- parser fixtures
- auth flow
- upload flow
- retrieval APIs

### Phase 6.2: Frontend Tests

- auth screens
- upload flow
- visualization state handling

### Phase 6.3: Operational Readiness

- health probes
- structured logging
- OTEL environment wiring
- local and cluster smoke tests

## Initial Implementation Focus

The first implementation slice should deliver:

1. Monorepo scaffolding
2. FastAPI backend foundation
3. React frontend foundation
4. Local Postgres + app development stack
5. Initial Helm / deployment skeleton

## Known Technical Notes

- Current sample COBB exports appear structurally consistent across the provided files.
- The sample CSVs include non-UTF-8 characters in headers, so parser code must not assume UTF-8-only decoding.
- Existing `tekton-ci` templates in `lucas_engineering` currently need a small enhancement to pass per-service `dockerfile` and `context` overrides for a single-repo / multi-image build setup.
