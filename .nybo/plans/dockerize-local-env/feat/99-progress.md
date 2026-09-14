# Progress — Dockerizar el Entorno Local

## Checklist

### Tasks
- [x] T1 — Backend Dockerfile, DATABASE_URL y compatibilidad PostgreSQL
- [x] T2 — Frontend Dockerfile y proxy env-aware
- [x] T3 — docker-compose.yml: orquestación de los 3 servicios
- [x] T4 — Makefile y documentación de uso local

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — `make up` levanta los 3 servicios y /health responde 200
- [x] `[TC-002]` *[INTEGRATION]* — Un dato registrado vía API persiste en el Postgres del contenedor
- [x] `[TC-003]` *[UNIT]* — Sin DATABASE_URL, el backend sigue usando sqlite:///:memory:
- [x] `[TC-004]` *[INTEGRATION]* — Las 4 migraciones corren limpias contra PostgreSQL real
- [~] `[TC-005]` *[E2E]* — Crear casa desde el frontend dockerizado llega al backend dockerizado — pata de proxy HTTP verificada (Vite dev server dockerizado → backend dockerizado, dato persistido en Postgres real); NO se automatizó el navegador/formulario real — pendiente de confirmación humana o de un run de e2e-explorer/e2e-build.
- [x] `[TC-006]` *[INTEGRATION]* — `make test` corre la suite de pytest y reporta resultado

## Completion Summary
Las 4 tasks implementadas y verificadas con un daemon Docker real
(disponible en este entorno de build, a diferencia de lo asumido al
despachar el build). `docker build` para ambos Dockerfiles, `docker
compose up` completo, `make up/down/build/logs/test/migrate`, y las 6
suites de pytest (90 tests) corrieron de verdad, no solo se revisaron
estáticamente. TC-001 a TC-004 y TC-006 en verde con evidencia de
ejecución real. TC-005 en verde para su pata de proxy HTTP (verificada
con curl real a través del proxy de Vite dockerizado hasta el backend
dockerizado, con persistencia confirmada en Postgres); el flujo de UI en
el navegador no fue accionado por esta build — ver
evidence/1/build-results.md.

Nota de entorno: gran parte del tiempo de build se fue diagnosticando
fallas intermitentes de TC-002 que resultaron ser causadas por procesos
nativos (no-Docker) ya escuchando en los puertos 8000/5173 en este
sandbox compartido, ajenos a esta sesión — no un defecto de la
configuración Docker/compose. Ver Observations en build-results.md.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 6 test cases. |
| 2 | 2026-09-11 | build | T1-T4 | TC-001..TC-004, TC-006 | Implementadas y verificadas con Docker real (backend/frontend Dockerfiles, docker-compose.yml, Makefile, README). |
| 3 | 2026-09-11 | verify | — | TC-001..TC-006 | Verificación end-to-end vía tests/integration/infra/*.test.sh + pytest/vitest reales. TC-005 solo pata de proxy HTTP, no UI de navegador. |
