---
feature: gastos-sin-reparto
schema: build-results/2
cycle: 1
updated: '2026-09-16T16:34:23.980Z'
exit: ready
verdict: verified
observations:
  entries: 2
judgment:
  entries: 2
tests:
  pytest:
    passed: 267
    failed: 0
    skipped: 1
  vitest:
    passed: 105
    failed: 0
build: pass
lint: pass
curated: true
---
### Goal

Implementar el pivote conceptual: un Gasto deja de repartirse entre participantes y de generar deuda interpersonal — pasa a ser una salida de fondos de la casa. Eliminar GastoParticipante (modelo, tabla, migracion) por completo; reescribir balance_service para exponer BalanceCasa {totales, aportes} sin ningun campo de deuda ni transferencia; actualizar API/dashboard/frontend al nuevo contrato. 4 tareas (T1-T4), 8 test cases (TC-001..TC-008).

### Judgment

- **J001** Deleted `tests/integration/services/gasto_service.test.py` in its entirety (T1's grep-driven test-update scope) rather than editing it: its single test (`test_nuevo_miembro_no_altera_gastos_ya_registrados`, TC-009 from a prior spec) exercised nothing but participant-list stability across a membership change — a concept that no longer exists once `Gasto` has no participants at all. Kept, not deleted: every test file where the grep hit covered a real behavior in addition to participants (e.g. `gasto_cuotas.test.py`'s cuota-shape assertions) — only the `participantes=` kwarg was stripped from those. Task-file criterion ('no eliminado sin reemplazo si cubria otra cosa ademas del reparto') applied literally: this file covered nothing else.
- **J002** Updated `src/frontend/api/dashboardClient.ts` (its `DashboardCasa.balance` field and its import of `BalancePorMiembro` from `gastosClient.ts`) even though it appears in no task file's Scope — T3/T4 changed `balance_service.calcular_balance`'s return type and `gastosClient.ts`'s exported types, and `dashboardClient.ts` is a direct, unavoidable consumer of both; leaving it unchanged would not compile (`tsc --noEmit` in `npm run build`). Classified as an in-authority `spec-deviation` (L2 semi-autonomous settles this class) rather than parked in `decisions.yaml`: it's a mechanical consequence of T3's own contract change, not a new design decision.

### Observations

- T1: grep de `GastoParticipante`/`.participantes`/`participantes=` en tests/ y src/ encontró 13 archivos ademas de los 4 de produccion listados en el task file (tests/unit/db/gasto.test.py, tests/unit/services/gasto_service.test.py, tests/integration/services/{gasto_service,gasto_moneda,gasto_cuotas,gasto_estado,balance_mensual}.test.py, tests/integration/api/{gastos_routes,gastos_moneda_routes}.test.py, tests/unit/services/{balance_service,balance_moneda,dashboard_service}.test.py, tests/unit/frontend/{Gastos,InicioCasa}.test.tsx) — todos actualizados o, cuando el test ya no cubria nada mas que reparto, eliminados (tests/integration/services/gasto_service.test.py completo — su unico test, TC-009 de una spec anterior, solo probaba estabilidad de participantes).
- T2/T3/T4: dashboard_service.DashboardCasa.balance y DashboardOut.balance cambiaron de List[BalancePorMiembro] a BalanceCasa (objeto, no lista) — todo consumidor (tests, InicioCasa.tsx) tuvo que ajustar de `balance[0].x`/`balance.filter(...)` a `balance.totales`/`balance.aportes`. dashboardClient.ts (frontend) no estaba en el scope de ningun task file pero importaba BalancePorMiembro de gastosClient.ts — actualizado como consecuencia directa del cambio de contrato, no un scope creep.

### Verification

**Build**: `npm run build` (`tsc --noEmit && vite build`) — green, no errors.

**Lint**: `npm run lint` (`eslint src/frontend --ext .ts,.tsx`) — green, no warnings.

**Tests**: `python3 -m pytest tests/` — 267 passed, 1 skipped (`test_dsn_externa_nunca_se_toca_directamente`, requires `DATABASE_URL` pointing at a real Postgres — environment-gated, not a gap in this cycle). `npm run test -- --run` (vitest) — 105 passed, 0 failed, across 18 files.

**Test cases (TC-001..TC-008)**:
- TC-001 `[INTEGRATION]` — `tests/unit/services/gasto_service.test.py::test_registrar_gasto_no_acepta_participantes_ni_genera_reparto` (passing `participantes=` raises `TypeError`) + `tests/integration/api/gastos_routes.test.py::test_registrar_gasto_con_participantes_en_el_body_los_ignora` (a payload with `participantes` is silently ignored, never generates a repartition row).
- TC-002 `[INTEGRATION]` — `tests/integration/db/postgres_migrations.test.py::test_migracion_0014_elimina_gasto_participantes_de_una_base_preexistente` (a Postgres DB with a pre-existing `gasto_participantes` table loses it after `run_migrations`, idempotent on a second run) + the fresh-DB assertion in `test_las_4_migraciones_corren_limpias_contra_postgres_real`.
- TC-003 `[INTEGRATION]` — `tests/unit/services/balance_service.test.py::test_tc003_total_gastado_de_la_casa_por_moneda` / `test_tc003_ars_siempre_presente_incluso_sin_actividad` + `tests/unit/services/balance_moneda.test.py::test_tc003_totales_separados_por_moneda_con_actividad_en_ambas`.
- TC-004 `[INTEGRATION]` — `tests/unit/services/balance_service.test.py::test_tc004_aporte_por_miembro_sin_ningun_campo_de_deuda` / `test_tc004_aporte_incluye_todo_miembro_de_la_casa_incluso_en_cero` + `tests/unit/services/balance_moneda.test.py::test_tc004_aportes_separados_por_moneda_con_actividad_en_ambas`.
- TC-005 `[UNIT]` — `tests/unit/services/balance_service.test.py::test_tc005_balance_casa_no_expone_ninguna_transferencia` (asserts `sugerir_transferencias`/`Transferencia`/`BalancePorMiembro` no longer exist in `balance_service`, and `BalanceCasa`'s only fields are `totales`/`aportes`).
- TC-006 `[UNIT]` — `tests/unit/frontend/Gastos.test.tsx::"TC-006: el formulario 'Nuevo gasto' no muestra ningún selector de participantes ni 'Todos los miembros'"`.
- TC-007 `[UNIT]` — `tests/unit/frontend/InicioCasa.test.tsx::"TC-007: la sección Balance muestra el nuevo total de la casa en ARS, sin ninguna cifra de deuda por miembro"`.
- TC-008 `[INTEGRATION]` — `tests/integration/services/gasto_cuotas.test.py` (all TC-001..TC-006 of that file, unchanged shape minus `participantes=`) + live smoke below confirms 3 cuotas of $40,000 each with no repartition.

**Coverage**: no coverage tool configured for this project (`stack.yaml`'s `quality_tools.coverage.tool: null`) — not a gap introduced by this cycle.

**Migration idempotency (real Postgres)**: ran against a real `postgres:16-alpine` container via Docker (`tests/integration/db/postgres_migrations.test.py`, the project's own ephemeral-container fixture) — `run_migrations` ran 3x clean on a fresh DB, and the new `test_migracion_0014_elimina_gasto_participantes_de_una_base_preexistente` test manually pre-created a legacy `gasto_participantes` table (CHAR(36) FKs, matching [DBG-03]'s convention) and confirmed migration 0014 drops it, idempotently, without touching `gastos`/`casas`/`miembros`.

**Live evidence**: `stack.yaml`'s documented `make up` conflicted on host ports 8000/5173 with an already-running, unrelated `gastos-test-*` compose stack (a different, pre-existing environment on this host — left untouched, never torn down). Ran the scoped equivalent instead: brought up only this worktree's `db` service via a temporary `docker-compose.override.yml` publishing Postgres on host port 5433 (removed after the run, never committed), then ran the backend directly with `python3 -m uvicorn src.api.main:app` pointed at that container. Full live route: registro → login → crear casa → crear categoría → `POST /gastos` with `participantes` in the body → confirmed the response has no `participantes` field and no repartition occurred → `GET /balance?mes=2026-01` returned exactly `{totales, aportes}` (no `balances`/`transferencias`) → `GET /inicio` dashboard's `balance` field carries the same new contract → registered a 3-cuota gasto and confirmed 3 rows of $40,000 each (TC-008 regression, live). Container and its volume were destroyed after the run (`docker compose down`); no persisted dev data was touched.

**Judgment log**: see below — two deviations recorded (deleting an obsolete test file entirely rather than partially, and touching `dashboardClient.ts` though it wasn't in any task file's Scope).

**Security**: no new attack surface — `GastoCreate` narrows (loses `participantes`), no new endpoint, no new external dependency, no secret/credential handling changed.

**Design principles**: consistent with the project's existing conventions — `_dividir_importe` kept as a general N-way split utility (still used for cuotas), currency-separation convention ([SERVP-05]-adjacent) reused unchanged for the new `totales`/`aportes` split, and the migration follows the existing raw-SQL `DROP TABLE IF EXISTS` idempotency pattern (inverse of the additive `ADD COLUMN IF NOT EXISTS` migrations already in this codebase).

**Wiki alignment**: `spec.md`/`00-overview.md` describe exactly the shape implemented; no drift.

### Curation

Two domain-memory additions from this cycle:

- `.nybo/memory/domains/db.md` **[DBP-02]** — the project's first *subtractive* migration pattern (delete the model class, remove it from its creating migration's `TABLES`, add a `DROP TABLE IF EXISTS` migration) — mirrors the existing additive-migration convention, confirmed live against a real Postgres pre-seeded with the legacy table.
- `.nybo/memory/domains/services.md` **[SERVP-06]** — when a service's return type changes shape (not additively), grep the whole repo for the old type/field names before calling the task done; this cycle's own task file didn't list `dashboardClient.ts`, a real consumer that would have broken the build.
- `.nybo/memory/domains/testing.md` **[TEST-02]** — a worktree's live smoke conflicts on host ports with the main checkout's own `make up`; documents the safe workaround (scoped `docker-compose.override.yml` for a port-less service only, backend run as a local process) and the "ports merge by concatenation, not replacement" gotcha inside that workaround.

No new ADRs, no conventions.yaml changes, no new domain files — all three land as narrow, high-confidence additions to existing domain files.
