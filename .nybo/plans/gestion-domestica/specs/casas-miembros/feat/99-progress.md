# Progress — Casas y Miembros

## Checklist

### Tasks
- [x] T1 — Data Layer: Casa y Miembro
- [x] T2 — Service Layer: Casas, Miembros y Roles
- [x] T3 — API Routes: Casas y Miembros
- [x] T4 — UI: Creación de Casa y Gestión de Miembros

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes (ver evidence/cycle-1/build-results.md → Observations, evidence/suggestions.yaml)

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Crear casa con nombre válido asigna admin al creador
- [x] `[TC-002]` *[UNIT]* — Crear casa sin nombre es rechazado
- [x] `[TC-003]` *[UNIT]* — Admin agrega miembro válido
- [x] `[TC-004]` *[UNIT]* — Identificación duplicada dentro de la misma casa es rechazada
- [x] `[TC-005]` *[INTEGRATION]* — Desactivar miembro preserva su historial
- [x] `[TC-006]` *[UNIT]* — Miembro sin rol admin no puede agregar miembros
- [x] `[TC-007]` *[UNIT]* — Admin consulta todos los gastos sin restricción
- [x] `[TC-008]` *[INTEGRATION]* — Usuario sin casa no puede registrar gasto
- [x] `[TC-009]` *[INTEGRATION]* — Dos casas mantienen datos independientes

## Completion Summary
All 4 tasks implemented via TDD in one build cycle. Backend (FastAPI +
SQLAlchemy 2.0, tests via pytest against in-memory SQLite) and frontend
(Vite + React + TS, tests via Vitest) scaffolded from scratch — this is
the first spec built in the repo. Spec-level verify: 20 backend tests +
4 frontend tests green, `npm run build` and `npm run lint` clean, all 9
test cases traced to a passing assertion. No escalated blockers; no open
`evidence/decisions.yaml` entries. Full judgment trail in
`evidence/cycle-1/build-results.md`.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 9 test cases. |
| 2 | 2026-09-11 | build | T1 | TC-001,TC-002,TC-004,TC-009 | Data layer: Casa/Miembro models, GUID type, migration. 4/4 tests green. |
| 3 | 2026-09-11 | build | T2 | TC-001..TC-009 | Service layer: casa_service, miembro_service, permisos. 11/11 tests green. |
| 4 | 2026-09-11 | build | T3 | TC-006,TC-007 | API routes: casas_router (FastAPI). 5/5 tests green. |
| 5 | 2026-09-11 | build | T4 | TC-004,TC-006 | UI: CrearCasa, Miembros pages + casasClient. 4/4 tests green. |
| 6 | 2026-09-11 | verify | — | TC-001..TC-009 | Spec-level verify: full suite green, build + lint clean. |
| 7 | 2026-09-11 | curate | — | — | Observations/suggestions extracted to evidence/. |
