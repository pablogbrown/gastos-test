# Domain: testing

## [TEST-01] Live/dev environment — dockerized backend+db+frontend
- **What**: local dev stack runs via `make up` (`docker compose up --build`) — services `db` (Postgres 16), `backend` (FastAPI/uvicorn, `--reload`, bind-mounts `./src` and `./tests`), `frontend` (Vite, bind-mounts `./src/frontend`).
- **Reach it**: backend at `http://localhost:8000` (OpenAPI at `/openapi.json`, docs at `/docs`); frontend at `http://localhost:5173`. `docker ps` to confirm containers are up before assuming a cold start is needed — `backend`'s `--reload` picks up source edits live, no rebuild needed for a Python-only change.
- **Auth**: `POST /auth/registro` `{email, password, nombre?}` → 201; `POST /auth/login` `{email, password}` → `{access_token, token_type}`. Use `Authorization: Bearer <access_token>` on every subsequent call. No seeded/fixture users — register fresh ones per smoke run.
- **Seeding data preexisting-to-a-fix directly in Postgres**: `docker exec gastos-test-db-1 psql -U taskia -d taskia -c "<SQL>"`. `rolenum` enum values are uppercase (`ADMIN`/`MEMBER`), not lowercase, despite the Python-side `RolEnum` values being lowercase strings — SQLAlchemy maps the Python enum *member name* to the Postgres enum label, not the Python value.
- **Cold start** (if containers are down): `make up` (or `docker compose up --build`) from repo root, using `.env` copied from `.env.example`. `make migrate` applies migrations against the running `db` service if needed.
- **Backend test command**: `.venv/bin/python -m pytest tests/` (or `make test` inside the container). Frontend: `npm run test` (vitest), `npm run build` (tsc + vite build), `npm run lint` (eslint on `src/frontend`).
- Discovered during `/nybo-verify --auto` for `fix-membresia-duplicada-actor-2026-09-14` (2026-09-14) — `stack.yaml`'s `dev_runbook` had no `cold_start`/`smoke` recorded yet; recommend `/nybo-brownfield-bootstrap --runbook` to formalize this into `stack.yaml` itself.
