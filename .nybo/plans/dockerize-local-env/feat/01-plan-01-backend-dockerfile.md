# Task 1 — Backend Dockerfile, DATABASE_URL y compatibilidad PostgreSQL

## Scope
- `Dockerfile.backend` — imagen del backend.
- `src/db/base.py` — sin cambios de comportamiento, solo confirmar (con test) que el fallback a SQLite sigue intacto cuando no hay `DATABASE_URL`.
- `.dockerignore` — excluir `.venv/`, `__pycache__/`, `node_modules/`, `.git/`.

## Changes
### Data Layer / Infra
- `Dockerfile.backend`: imagen base `python:3.12-slim`, copia `requirements.txt`/`requirements-dev.txt`, instala dependencias (incluye `psycopg2-binary`, ya presente), copia el código, expone el puerto 8000, comando `uvicorn src.api.main:app --host 0.0.0.0 --reload`.
- Verificación de compatibilidad Postgres (TC-004): levantar un Postgres real (vía Docker o el `docker-compose` de T3 si ya existe al momento de esta task) y correr `run_migrations` (`src/db/migrate.py`, ya existente) contra él — confirmar que `GUID` y el `Enum` de `RolEnum` crean tipo/tabla sin error. Si aparece algún problema de dialecto, corregirlo aquí (scope de esta task, no de T3).
- Confirmar que `src/db/base.py` sigue usando `sqlite:///:memory:` cuando `DATABASE_URL` no está seteada (TC-003) — no debería requerir cambios de código, solo un test que lo pruebe explícitamente si no existe ya uno.

## Design Rationale
Aislar la verificación de compatibilidad con Postgres en su propia task (antes de que exista `docker-compose`) evita descubrir un problema de dialecto recién en T3, cuando ya hay más piezas moviéndose.

## Dependencies
Ninguna — primer task de la spec.

## Done When
- [ ] TC-002, TC-003, TC-004 pasan.
- [ ] La imagen del backend construye (`docker build -f Dockerfile.backend .`) sin error.
- [ ] Las 4 migraciones corren limpias contra un Postgres real.

## Interfaces Produced
Ninguno (no se exportan símbolos de Python nuevos — es infraestructura).

## Standalone Verifiable
Sí — se puede construir y correr la imagen del backend contra un Postgres levantado ad-hoc, sin depender de T2/T3.
