# Progress — Gestión de Tareas y Puntos

## Checklist

### Tasks
- [x] T1 — Data Layer: Tarea e Historial
- [x] T2 — Service Layer: Tareas, Puntos y Ranking
- [x] T3 — API Routes: Tareas y Ranking
- [x] T4 — UI: Tareas, Ranking e Historial

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Crear tarea con nombre y puntos válidos
- [x] `[TC-002]` *[UNIT]* — Crear tarea sin nombre es rechazado
- [x] `[TC-003]` *[UNIT]* — Tarea nueva queda en estado Pendiente
- [x] `[TC-004]` *[UNIT]* — Tarea sin responsable puede completarla cualquier miembro
- [x] `[TC-005]` *[UNIT]* — Completar tarea registra quién, cuándo y otorga puntos
- [x] `[TC-006]` *[UNIT]* — No se otorgan puntos dos veces por la misma finalización
- [x] `[TC-007]` *[UNIT]* — Puntos acumulados de un miembro se calculan correctamente
- [x] `[TC-008]` *[UNIT]* — Ranking ordenado de mayor a menor puntaje
- [x] `[TC-009]` *[INTEGRATION]* — Tarea recurrente genera nueva instancia al completarse
- [x] `[TC-010]` *[INTEGRATION]* — Historial conserva registros de miembros desactivados

## Completion Summary
All 4 tasks implemented via TDD across one cycle; spec-level verify
passed on the first pass (no escalated blockers, no open decisions).
Backend: 47/47 pytest green (27 new). Frontend: 10/10 vitest green (6
new). `npm run build`/`npm run lint` clean. All 10 test cases covered.
A live end-to-end smoke run against a real uvicorn process + file-backed
SQLite reproduced `feat/10-verify.md`'s full 5-step scenario. See
`evidence/cycle-1/build-results.md` for the full judgment log and
`evidence/suggestions.yaml` for carried-forward/new observations.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 10 test cases. |
| 2 | 2026-09-11 | build | T1 | tests/unit/db/tarea.test.py | Tarea/HistorialTarea models + migration 0003; TC-003 green. |
| 3 | 2026-09-11 | build | T2 | tests/unit/services/tarea_service.test.py, tests/unit/services/ranking_service.test.py | crear_tarea/completar_tarea/procesar_recurrencia/calcular_ranking; TC-001,002,004-009 green. |
| 4 | 2026-09-11 | build | T3 | tests/integration/api/tareas_routes.test.py | tareas_router (create/list/patch/historial/ranking); TC-010 green, 400/409 contracts verified. |
| 5 | 2026-09-11 | build | T4 | tests/unit/frontend/Tareas.test.tsx | Tareas.tsx, Ranking.tsx, tareasClient.ts; build/lint clean. |
| 6 | 2026-09-11 | verify | — | full suite | Spec-level verify: 47 pytest + 10 vitest green, build/lint clean, live E2E smoke matches feat/10-verify.md. |
| 7 | 2026-09-11 | curate | — | — | Observations recorded in evidence/suggestions.yaml and build-results.md. |
