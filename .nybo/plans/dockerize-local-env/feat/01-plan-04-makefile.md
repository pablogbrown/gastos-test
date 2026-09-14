# Task 4 — Makefile y documentación de uso local

## Scope
- `Makefile` — comandos de uso diario.
- `README.md` — sección "Desarrollo local con Docker".

## Changes
### Infra / Docs
- `Makefile` con al menos:
  - `make up` → `docker compose up --build`
  - `make down` → `docker compose down`
  - `make build` → `docker compose build`
  - `make logs` → `docker compose logs -f`
  - `make test` → `docker compose exec backend python3 -m pytest`
  - `make migrate` → `docker compose exec backend python3 -c "from src.db.base import engine; from src.db.migrate import run_migrations; run_migrations(engine)"`
- `README.md`: sección nueva con los prerequisitos (Docker + Docker Compose) y los comandos `make` disponibles, reemplazando/complementando las instrucciones manuales de venv/npm ya existentes (esas quedan como alternativa sin Docker).

## Design Rationale
Envolver `docker compose` en `make` evita que cada desarrollador tenga que recordar flags (`--build`, `-f`, `exec backend ...`) — un solo punto de entrada documentado.

## Dependencies
T3 (`docker-compose.yml` debe existir para que estos comandos tengan algo que orquestar).

## Done When
- [ ] TC-006 pasa (`make test` corre la suite y reporta resultado).
- [ ] `make up` / `make down` / `make logs` / `make migrate` funcionan contra el `docker-compose.yml` de T3.
- [ ] README actualizado y coherente con los comandos reales del Makefile.

## Interfaces Produced
Ninguno.

## Standalone Verifiable
Sí, una vez T3 existe.
