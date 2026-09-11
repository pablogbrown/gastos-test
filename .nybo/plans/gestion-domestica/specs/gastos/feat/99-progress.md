# Progress — Gestión de Gastos

## Checklist

### Tasks
- [x] T1 — Data Layer: Gasto, Categoría y Participantes
- [x] T2 — Service Layer: Registro, División y Balance
- [x] T3 — API Routes: Gastos y Balance
- [x] T4 — UI: Registro de Gasto, Balance e Historial

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Registrar gasto con datos válidos
- [x] `[TC-002]` *[UNIT]* — Gasto sin categoría es rechazado
- [x] `[TC-003]` *[UNIT]* — No-admin no puede crear categoría
- [x] `[TC-004]` *[UNIT]* — Gasto sin participantes explícitos se divide entre todos los activos
- [x] `[TC-005]` *[UNIT]* — Gasto con participantes explícitos solo los afecta a ellos
- [x] `[TC-006]` *[UNIT]* — División de $40.000 entre 4 participantes da $10.000 c/u
- [x] `[TC-007]` *[UNIT]* — Balance calculado según el ejemplo del documento
- [x] `[TC-008]` *[UNIT]* — Transferencia sugerida entre deudor y acreedor
- [x] `[TC-009]` *[INTEGRATION]* — Nuevo miembro no altera gastos previos
- [x] `[TC-010]` *[INTEGRATION]* — Historial incluye gastos de miembros desactivados

## Completion Summary
Build converged in a single cycle (Cycle 1). All 4 tasks implemented via
TDD; all 10 test cases pass across unit/integration layers. Spec-level
verify: `python3 -m pytest` 43/43 green, `npm run test` (vitest) 8/8
green, `npm run build` and `npm run lint` clean. The 5-step End-to-End
Verification from `feat/10-verify.md` was executed manually against the
real FastAPI app (TestClient, no mocks beyond the SQLite test DB) and
passed without error. See `evidence/cycle-1/build-results.md` for full
execution detail and autonomous judgment calls;
`evidence/decisions.yaml` has no open items;
`evidence/suggestions.yaml` carries forward-looking observations for
`/nybo-curate`.

Not yet done: the `[HUMAN]`-tagged manual visual review of the
Gastos/Balance screens (`10-verify.md`'s Gate Criteria) — out of scope
for an autonomous build cycle, left for human sign-off.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 10 test cases. |
| 2 | 2026-09-11 | execute | T1 | — | Categoria/Gasto/GastoParticipante models + migration 0002 (seeds 8 predefined categories for pre-existing casas, idempotent). |
| 3 | 2026-09-11 | execute | T2 | TC-001..TC-009 | gasto_service/balance_service/categoria_service; registrar_gasto calls requiere_membresia_activa; permisos.puede reused for admin-only categoria creation. |
| 4 | 2026-09-11 | execute | T3 | TC-010 | gastos_router (categorias/gastos/balance), wired into src/api/main.py. |
| 5 | 2026-09-11 | execute | T4 | — | gastosClient.ts, Gastos.tsx, Balance.tsx; App.tsx navigation across Miembros/Gastos/Balance. |
| 6 | 2026-09-11 | verify | — | TC-001..TC-010 | Spec-level verify: 43/43 pytest, 8/8 vitest, build+lint clean, 5-step E2E walk passed. |
| 7 | 2026-09-11 | curate | — | — | Observations/suggestions recorded in evidence/suggestions.yaml; no new domain files created (reused casas-miembros conventions as-is). |
