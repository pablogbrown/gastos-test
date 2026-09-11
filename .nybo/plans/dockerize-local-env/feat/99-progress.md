# Progress — Dockerizar el Entorno Local

## Checklist

### Tasks
- [ ] T1 — Backend Dockerfile, DATABASE_URL y compatibilidad PostgreSQL
- [ ] T2 — Frontend Dockerfile y proxy env-aware
- [ ] T3 — docker-compose.yml: orquestación de los 3 servicios
- [ ] T4 — Makefile y documentación de uso local

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — `make up` levanta los 3 servicios y /health responde 200
- [ ] `[TC-002]` *[INTEGRATION]* — Un dato registrado vía API persiste en el Postgres del contenedor
- [ ] `[TC-003]` *[UNIT]* — Sin DATABASE_URL, el backend sigue usando sqlite:///:memory:
- [ ] `[TC-004]` *[INTEGRATION]* — Las 4 migraciones corren limpias contra PostgreSQL real
- [ ] `[TC-005]` *[E2E]* — Crear casa desde el frontend dockerizado llega al backend dockerizado
- [ ] `[TC-006]` *[INTEGRATION]* — `make test` corre la suite de pytest y reporta resultado

## Completion Summary
Not yet started.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 6 test cases. |
