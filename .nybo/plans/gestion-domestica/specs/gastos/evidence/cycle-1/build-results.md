# Build Results — gastos — Cycle 1

## Summary
All four tasks (T1-T4) implemented via TDD, spec-level verify passed on the
first cycle. No escalated blockers. Backend: 43/43 tests green (pytest,
including the 20 pre-existing `casas-miembros` tests, unaffected). Frontend:
8/8 tests green (vitest, including the 4 pre-existing `Miembros` tests).
`npm run build` and `npm run lint` clean. All 10 test cases (TC-001..TC-010)
covered across unit/integration layers, matching the mapping in
`feat/10-verify.md`. A full manual walk of the 5-step End-to-End
Verification in `feat/10-verify.md` (via `TestClient`, real router + real
service stack, no mocks) passed without error.

## Execution
| Task | Files | Tests | Result |
|---|---|---|---|
| T1 | src/db/models/{categoria,gasto}.py, src/db/migrations/0002_gastos.py | tests/unit/db/gasto.test.py (5) | green |
| T2 | src/services/{gasto_service,balance_service,categoria_service}.py | tests/unit/services/{gasto_service,balance_service}.test.py (9), tests/integration/services/gasto_service.test.py (1) | green |
| T3 | src/api/routes/gastos.py, src/api/main.py (router registration) | tests/integration/api/gastos_routes.test.py (6) | green |
| T4 | src/frontend/api/gastosClient.ts, src/frontend/pages/{Gastos,Balance}.tsx, src/frontend/App.tsx (navigation) | tests/unit/frontend/Gastos.test.tsx (4) | green |

Spec-level verify (`/nybo-verify --auto` equivalent, run once after all
tasks): build succeeded (`npm run build`: `tsc --noEmit` + `vite build`),
full test suite green (51/51 across both runners: 43 pytest + 8 vitest),
lint clean (`npm run lint`), all 10 TCs traced to at least one passing
test, and the 5-step End-to-End Verification from `feat/10-verify.md`
executed manually against the real FastAPI app (TestClient) with no
mocks beyond the SQLite test database.

## Judgment Section (autonomous decisions — trust level: semi-autonomous)

Trust level settles `spec-deviation` only; every entry below stayed
within that class or was a straightforward interface-filling decision
required to make the documented signatures runnable — none touched
security, schema-migration-as-a-new-tool, api-contract-breaking,
new-dependency, cost, or external-copy classes that this trust level
must defer.

1. **Reused `casas-miembros`'s guard/permisos exactly, no reimplementation.**
   `gasto_service.registrar_gasto` imports and calls
   `requiere_membresia_activa(casa_id, actor)` from
   `src.services.miembro_service` before any DB write, mirroring how that
   guard is documented to be consumed by sibling specs.
   `categoria_service.crear_categoria` reuses
   `src.services.permisos.puede(rol, "gestionar_categorias")` — the
   `gestionar_categorias` action was already present in
   `permisos.ACCIONES_ADMIN` from the `casas-miembros` build, so no edit
   to `permisos.py` was needed.
2. **`registrar_gasto`'s parameter order places `actor` before
   `participantes`**, not after it as literally written in
   `01-plan-02-service-layer.md` / `run-plan.json`
   (`..., pagado_por, participantes, actor`). Python requires
   non-default parameters before defaulted ones; `participantes` is the
   only optional argument (REQ-003's "sin especificar participantes"
   case), so it had to move last with a `None` default. All call sites
   (tests, API route) pass `participantes=` by keyword, so no caller
   depends on positional order.
3. **`pagado_por` defaults to `actor` at the API layer, not the service
   layer.** `00-overview.md`'s HTTP contract table for
   `POST .../gastos` lists only `{descripcion, importe, fecha,
   categoriaId, participantes?}` — no `pagadoPor` field — while REQ-001
   requires capturing "persona que lo realizó". Interpreted as: the
   person registering the expense is its payer by default (self-service
   registration, the common case); `pagado_por` is exposed as an
   optional field on `GastoCreate` so a future flow (e.g. an admin
   registering on behalf of someone) can override it without breaking
   the documented contract.
4. **`categoria_id` is `Optional[UUID] = None` on the `GastoCreate`
   Pydantic schema, not required.** Making it a required Pydantic field
   would make FastAPI reject a request missing `categoria_id` with a
   generic `422` before the request ever reaches
   `registrar_gasto`'s own `ValidationError` → `400` mapping. TC-002 and
   `10-verify.md`'s gate criteria explicitly expect **400** for "gasto sin
   categoría", so the schema defers that validation to the service.
5. **Pydantic request/response schemas for gastos live inline in
   `src/api/routes/gastos.py`**, not in `src/api/schemas.py`. T3's scope
   (fixed by `run-plan.json`) lists only `src/api/routes/gastos.py`;
   adding schemas there keeps this sub-spec's touched-files list
   accurate and avoids a merge-conflict surface on `schemas.py`, which
   belongs to the already-merged `casas-miembros` spec.
6. **Migration 0002 seeds the 8 predefined categories only for casas
   that already existed at migration time** (idempotent — re-running it
   does not duplicate). New casas created after this migration acquire
   their catalog through `crear_categoria` (REQ-002: the Administrator
   manages the catalog) rather than an automatic re-seed on casa
   creation, since `casa_service.crear_casa` is out of this sub-spec's
   file scope (owned by `casas-miembros`) and touching it was avoided
   per the task's explicit "import and reuse, do not reimplement"
   instruction. This satisfies T1's literal "Done When" bullet ("Seed de
   categorías corre sin duplicar en casas ya existentes").
7. **Added `listar_categorias(casa_id)` and `listar_gastos(casa_id)`**
   to `categoria_service.py`/`gasto_service.py` respectively. Neither is
   in T2's "Interfaces Produced" (no sibling spec consumes them), but
   both are needed so the GET routes in T3 stay thin adapters instead of
   querying the ORM directly from the route — same rationale
   `casas-miembros` used for its own `listar_miembros`.
8. **`gasto_service`/`balance_service`/`categoria_service` each open and
   close their own SQLAlchemy session** via `get_session()`, matching
   the pattern flagged in `casas-miembros`'s
   `evidence/suggestions.yaml` (`shared-session-per-request`) as the
   convention to follow until a request-scoped session is introduced.
   Not changed here — no cross-service transaction was required by any
   of this spec's test cases.
9. **No migration engine (Alembic) introduced**, per
   `casas-miembros`'s own `evidence/suggestions.yaml`
   (`adopt-alembic-on-second-migration`), which flagged this exact
   point ("once gastos... lands"). `0002_gastos.py` follows the same
   `upgrade(bind)`/`downgrade(bind)` over `Base.metadata` pattern as
   `0001_casas_miembros.py`. Re-flagged in this cycle's
   `suggestions.yaml` since a *third* migration (`tareas-puntos`,
   building concurrently) makes the case even stronger.
10. **`src/api/main.py` and `src/frontend/App.tsx` were touched even
    though neither is in any task's literal file scope.** Both already
    carry inline comments from the `casas-miembros` build anticipating
    this ("Las specs hermanas... agregarán su propio router/pantalla
    aquí"). Wiring `gastos_router` into `main.py` and adding
    Gastos/Balance navigation to `App.tsx` was necessary for
    `10-verify.md`'s End-to-End Verification section to be actually
    runnable against a live app, not just a synthetic `TestClient`
    assembled ad hoc in tests.
11. **Custom domain exceptions reused as-is** (`ValidationError`,
    `PermissionDeniedError`, `NotFoundError` from
    `src.services.exceptions`) — no new exception types were introduced
    for gastos/categorías/balance; the existing three already cover
    every failure mode in this spec's test cases.

## Observations (candidate conventions — for /nybo-curate)
- Confirms the `casas-miembros` suggestion `shared-session-per-request`
  is still open and now touched by a second spec — worth prioritizing
  before `tareas-puntos` (building concurrently) adds a third set of
  services doing the same open/close-per-call pattern.
- Confirms `adopt-alembic-on-second-migration` — this spec's
  `0002_gastos.py` is the second hand-rolled migration; a third
  (`tareas-puntos`, `0003_*`) is landing in parallel. Recommend
  introducing Alembic (or documenting the hand-rolled pattern as the
  permanent convention, if that's the deliberate choice) at the next
  feature-level integration point rather than per sub-spec.
- `python-lint-tool-undetected` (from `casas-miembros`) is still true;
  backend correctness continues to rest on `pytest` only, no
  ruff/flake8/mypy gate.
- The domain-agnostic HTTP helper pair (`ApiError`/`esApiError`/
  `parseJsonOrThrow`) originally written in `casasClient.ts` was reused
  (imported, not copy-pasted) by `gastosClient.ts`. Worth promoting to a
  shared `src/frontend/api/http.ts` once a third client (tareas-puntos)
  needs the same pattern, instead of each client re-declaring
  `parseJsonOrThrow`.

## Verification Evidence
- `python3 -m pytest -q` → 43 passed (T1: 5 new [+ existing db tests
  unaffected], T2: 10 new, T3: 6 new, plus all 20 pre-existing
  `casas-miembros` tests still green).
- `npm run test` (vitest) → 8 passed (4 new `Gastos.test.tsx` + 4
  pre-existing `Miembros.test.tsx`, unaffected).
- `npm run build` → `tsc --noEmit` clean, `vite build` succeeded.
- `npm run lint` → no ESLint errors/warnings.
- Manual TC-to-test mapping cross-checked against `feat/10-verify.md`
  and `feat/99-progress.md` — all 10 TCs have at least one passing
  assertion.
- 5-step End-to-End Verification from `feat/10-verify.md` executed
  against the real `FastAPI` app (`casas_router` + `gastos_router`) via
  `TestClient`, backed by a real SQLite DB running both migrations:
  registered a $75.000 gasto across 3 members, a $30.000 gasto across 2
  explicit participants, fetched `/balance` (transferencias sum
  reconciled against the payer's balance), added a new member and
  confirmed the original gasto's participant split was unchanged, then
  deactivated a member with a gasto and confirmed it remained in
  `/gastos`. All assertions passed.
