---
feature: gamificacion-puntos
schema: build-results/2
cycle: 1
updated: '2026-09-18T15:56:16.490Z'
exit: in-progress
verdict: pending
judgment:
  entries: 3
observations:
  entries: 1
tests:
  backend:
    passed: 388
    failed: 0
    excluded_pre_existing: 5
  frontend:
    passed: 150
    failed: 0
  postgres_migration:
    passed: 4
    failed: 0
build: pass
lint: pass
coverage: unavailable-not-configured
---
### Judgment

- **J002** (T4) The `GET /casas/{id}/logros` API returns only the raw `logro_id` string (matching `LogroObtenidoOut`, no name field in scope for T2) — `Ranking.tsx` duplicates a small local `NOMBRES_LOGRO` id->nombre map mirroring `logro_service.LOGROS_CATALOGO` purely for display, rather than adding a name field to the API response (kept the T2 API contract exactly as specified; matches this project's established convention of small per-layer duplicated helpers over new shared surface).
- **J003** (T4) `Miembros.tsx`'s "Meta de puntos mensual" field does not pre-fetch/display the casa's current meta value on mount (no `GET /casas/{id}` single-fetch endpoint exists) — implemented as a write-only field + Guardar button, consistent with the task's literal "campo + botón guardar" wording and TC-008's stated criterion ("Miembros permite a un Administrador editarla"), which does not require displaying the current value.
- **J004** (verify) Screen-level live evidence was skipped — no browser automation tool available in this dispatched session (no MCP browser tool in the session toolset; shell access to inspect/invoke a local Playwright binary was denied by the sandbox permission layer). Compensated with a full live API smoke chain (register->casa->complete task->ranking/logros/mes-filter->meta PATCH->dashboard, all against the real running dev stack) plus the full green frontend component test suite (150/150), rather than silently omitting screen capture. Recommend `/nybo-ui-evidence` or a manual look at Ranking/Miembros/Inicio as an optional next step.

### Observations

- `[GOTCHA]` `casa_service.actualizar_meta_puntos` must force-load `casa.miembros` (`_ = casa.miembros`) before returning, exactly like `crear_casa` already does — `CasaOut.miembros` triggers a lazy-load during FastAPI response serialization, which raises `DetachedInstanceError` once the service's own session is closed (`SessionLocal` has no `expire_on_commit=False`). Same shape as `[DBG-05]`'s Casa/relationship gotcha but for `Casa.miembros`, not a `to-many` collection returned as a nested resource.

### Verification

**Build**: `npm run build` (`tsc --noEmit && vite build`) — clean, no errors. Backend has no separate build step (Python).

**Tests**:
- Backend: `docker compose exec backend python -m pytest tests/ -q` — 388 passed. Excludes `tests/integration/infra/capacitor_config.test.py` (5 failures) — pre-existing on the base commit (`0c18dcd`), confirmed via `git stash` + re-run scoped to that file alone before excluding it; unrelated android/capacitor `.gitignore`/config gap from a prior merged feature, untouched by this diff.
- Postgres migration idempotency (`tests/integration/db/postgres_migrations.test.py`, real Postgres via docker-compose's `db` service): 4 passed, including new assertions for `logros_obtenidos` (FKs to `casas`/`miembros` confirmed real) and `casas.meta_puntos_mensual`; migration run 3x with no error (idempotent).
- Frontend: `npm run test -- --run` — 150 passed (22 files), including new/extended `Ranking.test.tsx` (7), `Miembros.test.tsx` (11), `InicioCasa.test.tsx` (13).
- `npm run lint` — clean.

**Coverage**: unavailable — not configured (`stack.yaml`'s `quality_tools.coverage.tool: null`, a pre-existing gap predating this feature, last checked 2026-09-11). Remedy: `/nybo-brownfield-bootstrap --quality`.

**Test cases & progress** — all 8 test cases in `spec.md` are `[INTEGRATION]`/`[UNIT]` (no `[MANUAL]`/`[E2E]` in this spec), all resolve to real, passing tests:
- TC-001 (niveles) — `gamificacion_ranking.test.py::test_niveles_cruzando_cada_umbral`.
- TC-002 (racha consecutiva) / TC-003 (mismo día no duplica / corte de racha) — `gamificacion_ranking.test.py::test_racha_consecutiva_se_acumula_sin_duplicar_por_dia`, `test_un_dia_sin_actividad_corta_la_racha`, plus edge cases (`test_racha_es_cero_sin_actividad_reciente`, `test_racha_es_cero_sin_ninguna_actividad`).
- TC-004 (ranking por mes, regresión dashboard) — `gamificacion_ranking.test.py::test_ranking_filtrado_por_mes_vs_sin_filtro`; regression covered by unmodified `tests/unit/services/dashboard_service.test.py` (17 passed) and `tests/unit/services/ranking_service.test.py`.
- TC-005 (logros, una sola vez) — `logros.test.py` (6 tests, incl. explicit double-call-no-duplicate and racha-based unlock).
- TC-006 (meta de la casa, admin-only, progreso correcto) — `meta_casa.test.py` (6 tests) + `casas_routes.test.py` (2 new HTTP-level tests, 403 for non-admin).
- TC-007 (frontend Ranking: mes/nivel/racha/logros) — `Ranking.test.tsx` (7 tests).
- TC-008 (frontend Inicio muestra meta; Miembros permite editarla) — `InicioCasa.test.tsx` (+2 tests) + `Miembros.test.tsx` (+4 tests).

**Manual test cases**: none in this spec.

**Live evidence**:
- API level (mandatory attempt, environment reachable — `stack.yaml`'s `dev_runbook`, `make up` stack already running): full live route driven against the real dev backend (`localhost:8000`) — registered a real user, created a casa, completed a 60-point task, confirmed `GET /ranking` returns `nivel: "Activo"` (crossed the 50pt threshold) and `racha: 1`; confirmed `GET /logros` shows `primera_tarea` unlocked; confirmed `GET /ranking?mes=<current>` matches, `?mes=2020-01` returns `[]`; configured `PATCH /casas/{id}/meta {"meta":100}` as the casa's own admin, confirmed `meta_puntos_mensual: 100` persisted; confirmed `GET /inicio` (dashboard) returns `metaCasa: {puntos_acumulados: 60, meta: 100, porcentaje: 60.0}`. Full REQ-001..REQ-005 chain proven live, not just via test doubles.
- Screen level: **skipped — no browser automation tool available in this dispatched session** (no MCP browser tool in this session's toolset, and shell access to inspect/invoke a local Playwright binary was denied by the sandbox permission layer). Substituted with the full frontend component-level test suite (150/150 green), including 3 files directly asserting the new UI renders the live-proven data shapes correctly (month selector defaulting to current month and re-querying on change, nivel chip + "🔥 N días", the Logros table, the "Meta de puntos mensual" field + save flow with success/error feedback, and the "Meta de la casa" `LinearProgress` card rendering only when `metaCasa` is non-null). This is recorded as a Judgment-log entry (below) rather than silently omitted.

**Judgment log** (this cycle, `evidence/1/build-results.md`): 3 entries (J001–J003, all in-authority `spec-deviation`-class implementation choices, documented above and in that file) — none require a human decision; all are conservative/documented defaults consistent with the task files' own wording and this project's established per-file-duplication convention.

**Security**: no new secrets, no new external dependency, no auth/authorization change beyond reusing the existing `_validar_actor_admin` guard pattern already established for admin-only actions.

**Design principles**: OOP/Clarity/Consistency — new persistence (`LogroObtenido`) follows the exact established model/migration/FK pattern (`ResumenTarjeta`-shape); no service duplicates persistence already owned by another service; `_rango_mes`/`_nivel_de` etc. follow the project's own "duplicate small per-service helpers" convention ([SERVP-02]).

**Wiki alignment**: none of this feature's changes are documented at `.nybo/memory/domains/` yet — deferred to curate (out of scope for this BUILD run per the user's explicit "do not run curate" instruction).

**Verdict**: **GREEN** — every automatable test case resolves to a real, passing test; build/lint/tests clean; live API evidence proves the whole REQ-001..REQ-005 chain end-to-end; the one live-evidence gap (screen-level capture) is named, substituted with strong compensating evidence, and does not block a `verified` result per this build's honest-degrade rule.
