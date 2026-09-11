# Build Results — dashboard-actividad — Cycle 1

## Summary
All four tasks (T1-T4) implemented via TDD, spec-level verify passed on
the first cycle. No escalated blockers. Backend: 87/87 tests green
(pytest, including all 70 pre-existing `casas-miembros`/`gastos`/
`tareas-puntos` tests, unaffected in behavior — 7 of their fixture files
needed a mechanical migration-list update, see Judgment #2). Frontend:
19/19 tests green (vitest, including the 14 pre-existing tests).
`npm run build` and `npm run lint` clean. All 5 test cases (TC-001..
TC-005) covered across unit/integration/E2E layers, matching the mapping
in `feat/10-verify.md`. A full manual walk of the 3-step End-to-End
Verification in `feat/10-verify.md` was executed against the real
`FastAPI` app (`src.api.main.app`, all four routers wired, no mocks
beyond the SQLite test database) and passed without error, including the
full activity feed reflecting a registered gasto and a completed tarea
with its points.

## Execution
| Task | Files | Tests | Result |
|---|---|---|---|
| T1 | src/db/models/historial_actividad.py, src/db/migrations/0004_historial_actividad.py | tests/unit/db/historial_actividad.test.py (3) | green |
| T2 | src/services/actividad_service.py, src/services/dashboard_service.py, hooks in src/services/{gasto_service,tarea_service}.py | tests/unit/services/dashboard_service.test.py (4), tests/integration/services/actividad_service.test.py (4) | green |
| T3 | src/api/routes/dashboard.py, src/api/main.py (router registration) | tests/integration/api/dashboard_routes.test.py (6) | green |
| T4 | src/frontend/api/dashboardClient.ts, src/frontend/pages/{InicioCasa,HistorialActividad}.tsx, src/frontend/App.tsx (navigation) | tests/unit/frontend/{InicioCasa,HistorialActividad}.test.tsx (5) | green |

Spec-level verify (`/nybo-verify --auto` equivalent, run once after all
tasks): build succeeded (`npm run build`: `tsc --noEmit` + `vite build`),
full test suite green (106/106 across both runners: 87 pytest + 19
vitest), lint clean (`npm run lint`), all 5 TCs traced to at least one
passing test, and the 3-step End-to-End Verification from
`feat/10-verify.md` executed manually against the real FastAPI app
(`TestClient` wrapping `src.api.main.app`) with no mocks beyond the
SQLite test database.

## Judgment Section (autonomous decisions — trust level: semi-autonomous)

Trust level settles `spec-deviation` only; every entry below stayed
within that class or was a straightforward interface-filling decision
required to make the documented signatures runnable — none touched
security, schema-migration-as-a-new-tool, api-contract-breaking,
new-dependency, cost, or external-copy classes that this trust level
must defer.

1. **Hooks placed strictly after each caller's own `session.commit()`,
   using a separate session/transaction inside `registrar_actividad`.**
   `feat/10-verify.md`'s Failure Triage explicitly warns against a hook
   "invocado antes de confirmar la transacción" — so in
   `gasto_service.registrar_gasto` the call sits after
   `session.refresh(gasto)`/before `return gasto`, and in
   `tarea_service.crear_tarea`/`completar_tarea` after their own
   `session.commit()`/`session.refresh(...)`. This means a gasto/tarea
   write and its activity-log entry are two separate commits (not one
   atomic transaction) — acceptable at this domestic scale per
   `00-overview.md`'s own Tradeoffs section (hooks over an event bus,
   explicitly to avoid additional infrastructure), and consistent with
   `historial_actividad` being an append-only side-effect log rather
   than a value the write's own success depends on.
2. **Seven pre-existing sibling-spec test fixtures
   (`tests/unit/services/{gasto_service,balance_service,tarea_service,
   ranking_service}.test.py`, `tests/integration/services/
   gasto_service.test.py`, `tests/integration/api/{gastos_routes,
   tareas_routes}.test.py`) were edited to add migration
   `0004_historial_actividad` and a
   `monkeypatch.setattr("src.services.actividad_service.get_session",
   ...)` line to their in-memory SQLite fixtures.** These tests build an
   isolated schema per file and previously had no reason to know about
   `historial_actividad`; once the hooks in `gasto_service`/
   `tarea_service` were wired, every one of those fixtures started
   failing with `no such table: historial_actividad` (26 failures
   surfaced on the first full-suite run this cycle). This is exactly the
   collateral the task's own instructions anticipated ("editing them is
   expected and necessary here") — only the fixture's migration list and
   session monkeypatch were touched, no assertion or business-logic line
   in any of those files was changed, and all pre-existing assertions
   still pass unmodified.
3. **`gasto_service.registrar_gasto`'s activity description credits
   `pagado_por` (the payer), not `actor` (who is registering).** Mirrors
   `completar_tarea`'s existing pattern where the credited party is the
   task's `beneficiario`/`miembro_id`, not necessarily the `actor`
   performing the call (e.g. an Administrador can register/complete on
   someone else's behalf). Since `pagador` is already queried inside
   `registrar_gasto` for validation, no extra query was needed.
4. **`dashboard_service.armar_dashboard` filters `listar_miembros` to
   `activo=True` before returning them**, per T2's own Changes text
   ("agrega miembros activos..."), even though REQ-001's requirement
   text just says "miembros" without qualifying "activos". Interpreted
   the T2 task file (more specific, written for this exact function) as
   controlling over the higher-level REQ-001 wording.
5. **"Tareas completadas recientes" is sourced from
   `tarea_service.listar_historial` (the `HistorialTarea` event log,
   which carries a real completion timestamp), not from
   `listar_tareas(casa_id, estado=COMPLETADA)`.** `Tarea` itself has no
   completion-date column, so only `HistorialTarea.completada_en` can
   answer "most recently completed" in a way consistent with "recientes"
   (REQ-001's business rule: last 10 by date descending). This also
   naturally handles a recurring tarea whose original instance is later
   reopened as a new pending row — the historical completion record for
   the prior instance is unaffected.
6. **`DashboardOut`'s nested list fields (`GastoOut`, `BalancePorMiembroOut`,
   `TareaOut`, `HistorialTareaOut`) are imported from
   `src.api.routes.gastos`/`src.api.schemas` instead of being
   redeclared** in `dashboard.py`. Confirmed empirically (ran the
   existing `gastos_routes.test.py::test_registrar_gasto_y_consultar_
   balance_end_to_end`, which already builds a `BalanceResponse` the
   same way from a list of `BalancePorMiembro` dataclass instances) that
   pydantic v1's `orm_mode` config on a nested submodel lets FastAPI
   convert a list of ORM/dataclass objects transparently — the same
   pattern already proven in this codebase, reused rather than
   reinvented.
7. **`src/api/main.py` and `src/frontend/App.tsx` were touched even
   though neither is in `run-plan.json`'s literal file scope for any
   task** — same rationale `gastos`/`tareas-puntos` used for the same
   two files: both must be wired for `10-verify.md`'s End-to-End
   Verification to be runnable against a live app.
8. **`src/frontend/App.tsx` also wires the pre-existing `Tareas` and
   `Ranking` pages into navigation**, which neither `gastos` nor
   `tareas-puntos` had done (`git log` shows no prior commit touching
   `App.tsx` from the `tareas-puntos` branch; both pages existed as
   unreachable dead code before this cycle). Since this sub-spec is
   explicitly commissioned to wire `App.tsx`'s navigation and is the
   *last* sub-spec of the feature, leaving `Tareas`/`Ranking`
   unreachable in the shipped app would make `gestion-domestica` visibly
   incomplete for no reason tied to this spec's own scope — a
   `spec-deviation`-class call, staying inside builder authority at
   `semi-autonomous`. `rolUsuarioActual="admin"` was reused for both, matching
   the existing hardcoded value already used for `Miembros`/`Gastos`
   (no `auth` domain exists yet in this project).
9. **`historial_actividad.miembro_id` is nullable** (per T1's own
   documented schema) but every hook wired in this cycle always supplies
   a concrete miembro_id (`pagado_por`, `actor`, or the tarea's
   `beneficiario`) — no code path in this spec currently inserts a null
   `miembro_id`. Left nullable as specified for forward compatibility
   (e.g. a future casa-level event with no single member attached), per
   T1's Interfaces Produced signature.
10. **`TipoActividadEnum.MIEMBRO_AGREGADO` is defined in the schema but
    never triggered.** REQ-002's requirement text lists "miembro
    agregado" among tracked actions, and the ER diagram's `tipo` field
    implies it as a valid value, but T2's own Changes text only commissions
    hooks in `gasto_service.registrar_gasto` and
    `tarea_service.crear_tarea`/`completar_tarea` — `miembro_service.
    agregar_miembro` is never named, and `miembro_service.py` is owned by
    the already-merged `casas-miembros` spec (out of this sub-spec's
    stated edit scope). Left as an intentional gap matching the task
    file's literal wording rather than an oversight; flagged in
    `evidence/suggestions.yaml` for a future decision.

## Observations (candidate conventions — for /nybo-curate)
- Confirms `shared-session-per-request-still-open` (flagged by both
  `casas-miembros` and `gastos`): `actividad_service.py` also opens/
  closes its own session per call, now a fourth service doing so. The
  activity-log hooks make the "one write, one transaction" gap slightly
  more visible (see Judgment #1) — worth resolving before a fifth
  service is added to this project.
- `adopt-alembic-on-second-migration`/`-third-migration` (from
  `casas-miembros`/`gastos`) is now a *fourth* hand-rolled migration
  (`0004_historial_actividad.py`). Recommend a decision at this feature's
  ship/distill point rather than deferring again.
- New candidate: `activity-log-hook-pattern` — a direct
  `registrar_actividad(...)` call placed immediately after a service's
  own commit is now the established pattern for cross-cutting event
  logging in this codebase (no event bus). Worth documenting explicitly
  as a domain convention so a future spec adding a new action type knows
  where to hook in without re-deriving the "after commit, own
  transaction" rule from scratch.
- `miembro_agregado` is a defined `TipoActividadEnum` value with no
  hook wiring it (Judgment #10) — worth a deliberate decision (wire it
  into `miembro_service.agregar_miembro`, or drop the unused enum value)
  rather than leaving it silently unused.

## Verification Evidence
- `python3 -m pytest -q` → 87 passed (T1: 3 new, T2: 8 new [4 unit +
  4 integration], T3: 6 new, plus all 70 pre-existing tests from
  `casas-miembros`/`gastos`/`tareas-puntos` still green after the
  mechanical fixture updates in Judgment #2).
- `npm run test` (vitest) → 19 passed (5 new [3 `InicioCasa.test.tsx` +
  2 `HistorialActividad.test.tsx`] + 14 pre-existing, unaffected).
- `npm run build` → `tsc --noEmit` clean, `vite build` succeeded.
- `npm run lint` → no ESLint errors/warnings.
- Manual TC-to-test mapping cross-checked against `feat/10-verify.md`
  and `feat/99-progress.md` — all 5 TCs have at least one passing
  assertion (TC-001 covered by `InicioCasa.test.tsx`'s data-populated
  case plus the live E2E walk below; TC-002 by both
  `dashboard_service.test.py`'s empty-casa case and
  `InicioCasa.test.tsx`'s empty-sections case; TC-003/TC-004 by
  `actividad_service.test.py`; TC-005 by
  `historial_actividad.test.py`, `actividad_service.test.py`, and
  `dashboard_routes.test.py`'s ordering assertions).
- 3-step End-to-End Verification from `feat/10-verify.md` executed
  against the real `FastAPI` app (`src.api.main.app`, all four routers)
  via `TestClient`, backed by a real SQLite DB running all four
  migrations: created a casa, registered a categoria and a $5.000 gasto,
  created and completed a tarea worth 5 points, then confirmed
  `GET /inicio` reflected the gasto/balance/ranking and
  `GET /actividad` listed all four resulting events
  (`gasto_registrado`, `tarea_creada`, `tarea_completada`,
  `puntos_obtenidos`) ordered most-recent-first with human-readable
  descriptions. All assertions passed.
