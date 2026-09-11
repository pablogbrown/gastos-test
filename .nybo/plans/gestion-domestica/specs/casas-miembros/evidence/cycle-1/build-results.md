# Build Results — casas-miembros — Cycle 1

## Summary
All four tasks (T1-T4) implemented via TDD, spec-level verify passed on the
first cycle. No escalated blockers. Backend: 20/20 tests green (pytest).
Frontend: 4/4 tests green (vitest). `npm run build` and `npm run lint`
clean. All 9 test cases (TC-001..TC-009) covered across unit/integration
layers, matching the mapping in `feat/10-verify.md`.

## Execution
| Task | Files | Tests | Result |
|---|---|---|---|
| T1 | src/db/types.py, src/db/base.py, src/db/models/{casa,miembro}.py, src/db/migrations/0001_casas_miembros.py | tests/unit/db/casa_miembro.test.py (4) | green |
| T2 | src/services/{exceptions,permisos,casa_service,miembro_service}.py | tests/unit/services/casa_service.test.py (4), tests/integration/services/miembro_service.test.py (7) | green |
| T3 | src/api/schemas.py, src/api/routes/casas.py, src/api/main.py | tests/integration/api/casas_routes.test.py (5) | green |
| T4 | src/frontend/{App,main}.tsx, src/frontend/pages/{CrearCasa,Miembros}.tsx, src/frontend/api/{casasClient,permisos}.ts, index.html, package.json, tsconfig.json, vite.config.ts, .eslintrc.cjs | tests/unit/frontend/Miembros.test.tsx (4) | green |

Spec-level verify (`/nybo-verify --auto` equivalent, run once after all
tasks): build succeeded (`npm run build`, `python3 -m py_compile`), full
test suite green (24/24 across both runners), lint clean
(`npm run lint`), all 9 TCs traced to at least one passing test.

## Judgment Section (autonomous decisions — trust level: semi-autonomous)

Trust level settles `spec-deviation` only; every entry below stayed
within that class or was a straightforward interface-filling decision
required to make the documented signatures runnable — none touched
security, schema-migration-as-a-new-tool, api-contract-breaking,
new-dependency-of-consequence, cost, or external-copy classes that this
trust level must defer.

1. **Project is greenfield — no scaffold existed.** Set up
   `requirements.txt`/`requirements-dev.txt` + `pytest.ini` for the
   Python backend (FastAPI + SQLAlchemy 2.0 + pydantic 1.x, chosen to
   match `.nybo/foundation/stack.yaml`'s `backend: Python`/`database:
   PostgreSQL`), and a Vite + React + TypeScript + Vitest scaffold for
   the frontend (`package.json`, `tsconfig.json`, `vite.config.ts`,
   `.eslintrc.cjs`, `index.html`) to match `frontend: React` and the
   root README's existing `npm install && npm run dev` Quick Start.
   `DATABASE_URL` defaults to an in-memory SQLite (portable `GUID`
   column type in `src/db/types.py`) so the test suite runs without a
   live PostgreSQL; production wiring is a plain env var.
2. **`pytest.ini` uses `--import-mode=importlib`.** The mandated test
   file names (`*.test.py`, e.g. `casa_miembro.test.py`) collide with
   pytest's default "prepend" import mode when `__init__.py` files are
   present in `tests/` (multi-dot filenames get misparsed into a nested
   package path). `--import-mode=importlib` resolves this without
   renaming the contract's test files.
3. **No migration engine (Alembic) introduced.**
   `src/db/migrations/0001_casas_miembros.py` exposes `upgrade(bind)` /
   `downgrade(bind)` operating directly on `Base.metadata` for the two
   tables this spec owns — satisfies "corre limpia sobre una base
   vacía" without adding a new tool. Introducing Alembic for real
   incremental migrations is a convention decision to make once a
   second migration is needed (flagged in `evidence/suggestions.yaml`).
4. **`Miembro.id` doubles as the cross-spec "usuario_id".** Neither the
   spec nor T2's "Interfaces Produced" define a separate `Usuario`
   entity (auth is out of scope for this sub-spec). `requiere_membresia_
   activa(casa_id, usuario_id)` checks for a `Miembro` row with
   `id=usuario_id` — i.e., the caller's external identity IS the
   member's row id within that casa. `crear_casa(nombre, usuario_creador)`
   creates the admin Miembro with `id=usuario_creador` for this reason.
   This is the only interpretation that satisfies every given signature
   without inventing an undocumented field.
5. **Default `nombre`/`identificacion` for the auto-created admin
   member.** `crear_casa`'s signature takes only the casa's `nombre`,
   not the creator's personal name. Used `"Administrador"` as a
   placeholder `nombre` and `str(usuario_creador)` as `identificacion`
   (guaranteed unique — it's the only member at creation time). A future
   auth/profile spec can update these without touching this contract.
6. **Auth placeholder on API routes: `X-Usuario-Id` header.** T3's scope
   is only `src/api/routes/casas.py`; there is no `auth` domain yet. All
   routes read the acting user from a required `X-Usuario-Id` header
   instead of a real session/token. Documented inline in `casas.py`'s
   module docstring as a seam for the future auth spec to replace.
   `Miembro`/service signatures (which sibling specs import) are
   unaffected by this choice.
7. **`PATCH .../miembros/{id}` rejects `{"activo": true}` with 400.**
   T2 only produces `desactivar_miembro` (one-directional). Reactivating
   a member has no backing service in this spec's contract, so the route
   returns 400 rather than silently doing nothing or inventing a
   `reactivar_miembro` service not in T2's "Interfaces Produced".
8. **Custom exception names instead of shadowing `PermissionError`.**
   `src/services/exceptions.py` defines `ValidationError`,
   `PermissionDeniedError`, `NotFoundError` — the spec's prose says
   "PermissionError" generically but it is not part of any documented
   interface signature, so a distinct name avoids colliding with
   Python's built-in OSError subclass of the same name.
9. **Added `listar_miembros(casa_id)` to `miembro_service.py`.** Not in
   T2's "Interfaces Produced" (no sibling spec consumes it) but needed
   so the GET route (T3) stays a thin adapter per T3's own Design
   Rationale, instead of querying the ORM model directly from the route.
10. **Frontend has no router.** `App.tsx` composes `CrearCasa`/`Miembros`
    with local state only (T4 doesn't list a router dependency and none
    exists yet). `usuarioId` is generated client-side via
    `crypto.randomUUID()` per session as an explicit stand-in until the
    auth spec exists — visible and documented in `App.tsx`, not hidden
    behind a fake login flow.

## Observations (candidate conventions — for /nybo-curate)
- This is the first spec in the repo; it establishes the backend layout
  (`src/db`, `src/services`, `src/api/routes`) and the SQLite-for-tests /
  Postgres-for-prod split via `DATABASE_URL` + a portable `GUID` column
  type — worth promoting to `.nybo/memory/domains/db.md` and
  `services.md` so `gastos` and `tareas-puntos` follow the same pattern.
- Service functions each open/close their own SQLAlchemy session
  (no request-scoped session injection yet) — sibling specs should
  follow this until a shared session-per-request pattern is introduced.
- `permisos.py`'s action-string table (`ACCIONES_ADMIN`/`ACCIONES_MIEMBRO`)
  is meant to be extended, not replaced, by `gastos`/`tareas-puntos` — new
  actions should be added to the existing sets there.
- No lint/coverage tool was detected for Python in `stack.yaml`
  (`quality_tools.lint: null`); only `npm run lint` (ESLint on
  `src/frontend`) is wired. Backend correctness currently rests on
  `pytest` + `py_compile` only.

## Verification Evidence
- `python3 -m pytest tests/ -q` → 20 passed (T1: 4, T2: 11, T3: 5).
- `npm run test` (vitest) → 4 passed.
- `npm run build` → `tsc --noEmit` clean, `vite build` succeeded.
- `npm run lint` → no ESLint errors/warnings.
- `python3 -m py_compile` over all `src/**/*.py` → clean.
- Manual TC-to-test mapping cross-checked against `feat/10-verify.md` and
  `feat/99-progress.md` — all 9 TCs have at least one passing assertion.
