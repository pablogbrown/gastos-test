# Task 3 — docker-compose.yml: orquestación de los 3 servicios

## Scope
- `docker-compose.yml` — servicios `db`, `backend`, `frontend`.
- `.env.example` — variables usadas por `docker-compose.yml` (con valores de ejemplo, no secretos reales).

## Changes
### Infra
- Servicio `db`: imagen `postgres:16-alpine`, variables `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` (via `.env`), volumen nombrado para persistencia, healthcheck (`pg_isready`).
- Servicio `backend`: build desde `Dockerfile.backend`, `DATABASE_URL=postgresql://...@db:5432/...` apuntando al servicio `db`, `depends_on: db (condition: service_healthy)`, volumen montando `./src` y `./tests` para hot-reload, puerto `8000:8000`.
- Servicio `frontend`: build desde `Dockerfile.frontend`, `VITE_API_PROXY_TARGET=http://backend:8000`, `depends_on: backend`, volumen montando `./src/frontend` para hot-reload, puerto `5173:5173`.
- Red común (`default` de compose alcanza, sin necesidad de una red custom) para que `backend`/`frontend` se resuelvan por nombre de servicio.

## Design Rationale
`depends_on` con `condition: service_healthy` (no solo orden de arranque) evita la carrera clásica de "el backend arranca antes de que Postgres acepte conexiones" — el healthcheck de `db` es la única señal confiable de que ya puede recibir queries.

## Dependencies
T1 (Dockerfile.backend debe existir), T2 (Dockerfile.frontend debe existir).

## Done When
- [ ] TC-001, TC-002, TC-005, TC-006 pasan.
- [ ] `docker compose up` levanta los 3 servicios sin error y `GET http://localhost:8000/health` responde 200.
- [ ] El frontend en `http://localhost:5173` puede crear una casa de punta a punta contra el backend dockerizado.

## Interfaces Produced
Ninguno.

## Standalone Verifiable
No completamente en aislamiento — requiere T1 y T2 ya construidos, pero una vez ambos existen, esta task se verifica de punta a punta por sí sola (`docker compose up` + smoke test).
