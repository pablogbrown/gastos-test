# Progress — Vista General y Actividad

## Checklist

### Tasks
- [x] T1 — Data Layer: Historial de Actividad
- [x] T2 — Service Layer: Registro de Actividad y Agregación del Dashboard
- [x] T3 — API Routes: Dashboard y Actividad
- [x] T4 — UI: Pantalla Principal e Historial de Actividad

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[E2E]* — Flujo completo del ejemplo del documento se refleja en inicio e historial
- [x] `[TC-002]` *[UNIT]* — Dashboard de una casa vacía no lanza error
- [x] `[TC-003]` *[INTEGRATION]* — Registrar un gasto agrega una entrada de actividad
- [x] `[TC-004]` *[INTEGRATION]* — Completar una tarea agrega entradas de actividad y puntos
- [x] `[TC-005]` *[UNIT]* — Historial de actividad ordenado de más reciente a más antiguo

## Completion Summary
Build converged in a single cycle (Cycle 1). All 4 tasks implemented via
TDD; all 5 test cases pass across unit/integration/E2E layers.
Spec-level verify: `python3 -m pytest` 87/87 green (including all 70
pre-existing `casas-miembros`/`gastos`/`tareas-puntos` tests), `npm run
test` (vitest) 19/19 green, `npm run build` and `npm run lint` clean.
The 3-step End-to-End Verification from `feat/10-verify.md` was executed
manually against the real FastAPI app (`TestClient` wrapping
`src.api.main.app`, no mocks beyond the SQLite test DB) and passed
without error. See `evidence/cycle-1/build-results.md` for full
execution detail and autonomous judgment calls (including why 7
sibling-spec test fixtures needed a mechanical migration-list update);
`evidence/decisions.yaml` has no open items; `evidence/suggestions.yaml`
carries forward-looking observations for `/nybo-curate`, including a
new `activity-log-hook-pattern` candidate convention.

Not yet done: the `[HUMAN]`-tagged manual visual review of the
Inicio/Historial de actividad screens (`10-verify.md`'s Gate Criteria) —
out of scope for an autonomous build cycle, left for human sign-off.
This is the final sub-spec of `gestion-domestica`; once reviewed, the
whole feature is ship-eligible.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 5 test cases. |
| 2 | 2026-09-11 | execute | T1 | — | HistorialActividad model (TipoActividadEnum) + migration 0004. |
| 3 | 2026-09-11 | execute | T2 | TC-002..TC-005 | actividad_service (registrar_actividad/obtener_actividad), dashboard_service (armar_dashboard); hooks added to gasto_service.registrar_gasto and tarea_service.crear_tarea/completar_tarea. |
| 4 | 2026-09-11 | execute | T3 | — | dashboard_router (/inicio, /actividad), wired into src/api/main.py. |
| 5 | 2026-09-11 | execute | T4 | TC-001 | dashboardClient.ts, InicioCasa.tsx, HistorialActividad.tsx; App.tsx navigation now covers all 7 screens across the feature (also wired the previously-unreachable Tareas/Ranking pages). |
| 6 | 2026-09-11 | verify | — | TC-001..TC-005 | Spec-level verify: 87/87 pytest, 19/19 vitest, build+lint clean, 3-step E2E walk passed against the real app. |
| 7 | 2026-09-11 | curate | — | — | Observations/suggestions recorded in evidence/suggestions.yaml; no new domain files created this cycle. |
