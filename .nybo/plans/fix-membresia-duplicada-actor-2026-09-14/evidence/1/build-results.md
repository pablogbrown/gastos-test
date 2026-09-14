---
feature: fix-membresia-duplicada-actor-2026-09-14
schema: build-results/2
cycle: 1
updated: '2026-09-14T16:42:29.492Z'
exit: ready
verdict: ready
judgment:
  entries: 2
build:
  status: pass
  errors: 0
  warnings: 0
tests:
  status: pass
  total: 191
  passed: 191
  failed: 0
  skipped: 0
integration:
  status: not-configured
  proven: 4
  total: 4
coverage:
  status: unavailable
  percent: null
  threshold: 80
  reason: not-configured
observations:
  entries: 1
---
### Goal

T1: agregar_miembro rechaza una segunda fila Miembro activa para el mismo (casa_id, usuario_id) en la misma casa (REQ-001). T2: resolver_actor_en_casa reemplaza .one_or_none() por .order_by(Miembro.id).first() para nunca crashear con MultipleResultsFound ante duplicados preexistentes (REQ-002).

### Judgment

- T1 implementado con .one_or_none() (antes del fix nunca puede existir >1 fila activa para el mismo (casa_id, usuario_id), por diseño — la validación recién se agrega). T2 implementado exactamente como especifica 01-plan-02-endurecer-resolver-actor.md: order_by(Miembro.id).first() en vez de .one_or_none(), sin agregar columna de timestamp (Miembro no la tiene) — orden estable por id, no arbitra cuál membresía es la 'correcta', solo elimina el 500. No hubo desviaciones del run-plan.json ni decisiones fuera de la autoridad de trust semi-autonomous (spec-deviation): ambos cambios siguen el contrato tal cual estaba escrito.
- **Verify J001** Judgment log double-read: reviewed both execute-phase entries from cycle 1 (T1 .one_or_none() rationale, T2 order_by(Miembro.id).first() rationale). Both reconfirmed — no code path found where the T1 pre-fix "at most one active row" assumption is violated at time of validation (the new check runs before insert, atomically within the same transaction), and T2's order_by(Miembro.id).first() was verified live against a real seeded duplicate in the dockerized Postgres environment: 5/5 repeated requests resolved consistently, 0/5 crashed with 500. 2 entries reviewed, 2 confirmed, 0 overturned.

### Observations

- `[NOTE]` No dedicated integration-test harness/command configured for this project (`stack.yaml` has no `testing:` key) — TC-001..TC-004 (all tagged [INTEGRATION]) run and pass as part of the single unified `pytest tests/` suite, since this project has no unit/integration test-runner split. Recommend `/nybo-brownfield-bootstrap --quality` to formalize a coverage tool and (optionally) a dedicated integration probe/command.

### Verification

- [x] Build: pass (0 warnings) — `npm run build` (tsc --noEmit && vite build), unaffected by this backend-only change.
- [x] Tests: 191/191 passing (0 failed) — 134 backend (`pytest tests/`, includes 4 new) + 57 frontend (`vitest run`).
- [x] Integration tests: 4/4 `[INTEGRATION]` cases proven · pass — no dedicated integration-test harness is configured in this project (`stack.yaml` has no `testing:` key); TC-001..TC-004 run and pass as part of the single unified `pytest tests/` suite (see Observations).
- [ ] Coverage: unavailable — not configured (`stack.yaml` `quality_tools.coverage.tool: null`, a recorded human decision — not re-litigated here per policy). Remedy: `/nybo-brownfield-bootstrap --quality` before the next build.
- [x] Test cases & progress: 2/2 tasks done, 4/4 automatable test cases covered — `[INTEGRATION]` TC-001, TC-002, TC-003, TC-004. No gaps.
- [x] `[E2E]` / `[MANUAL]` test cases: none in this spec.
- [x] Live evidence — **screen: n/a — outcome not visual** (this fix is backend/API-only, no UI surface touched) · **api: observed**. Driven against the actual dockerized dev environment already running (`docker ps` showed `db`/`backend`/`frontend` up; backend has `--reload` and had already picked up the source change). Route driven:
  1. Registered 2 real Usuarios via `POST /auth/registro`, logged in via `POST /auth/login`, created a Casa via `POST /casas`.
  2. `POST /casas/{id}/miembros` with the same email twice → 1st: 201, 2nd: **400** `"El usuario ya es miembro activo de esta casa."` (TC-001, live).
  3. Same Usuario added to two different Casas by email → both **201** (TC-002, live control case).
  4. Seeded a genuine preexisting duplicate `Miembro` row directly in Postgres via `docker exec ... psql` (bypassing the API/T1 on purpose, simulating pre-fix data — `rolenum` enum values are uppercase `ADMIN`/`MEMBER` at the DB level).
  5. Reproduced the **exact original incident**: the now-duplicated member attempted `PATCH .../miembros/{admin_id}` to deactivate the Administrador, repeated 5 times → **403 every time** (`"Solo un Administrador puede realizar esta acción."`), never 200 (TC-004, live, and directly closes the spec's stated authorization-incident concern).
  6. `GET /casas/{id}/miembros` as the duplicated user, repeated 5 times → **200 every time**, never 500 (TC-003, live).
  7. `docker logs gastos-test-backend-1 --since 3m` grepped for `500|Traceback|MultipleResultsFound|ERROR` → **zero matches** across the entire smoke run.
  This is not fixture-backed against a fake service — it is the real dockerized backend + real Postgres, the same environment the original QA session (spec.md Sources) used.
- [x] Judgment log: 2 entries reviewed, 2 confirmed, 0 overturned (see Verify J001 in Judgment section).
- [ ] Security: no security-scan tool configured (`stack.yaml` `quality_tools.security.tool: null`); not run.
- [x] Design principles: Single Responsibility preserved (validation colocated with existing `agregar_miembro` validations); Liskov-safe (`resolver_actor_en_casa`'s contract — returns `Miembro.id` or raises `PermissionDeniedError` — unchanged).
- [x] Wiki alignment: no user-visible capability change beyond a new 400 error message; no `wiki/` update needed.

### Fixed during verify
- none

Note: no dedicated security-scan or complexity tool configured for this project — see `stack.yaml` `quality_tools`.

### Curation

Curated 5 findings: 1 convention (`[SERV-01]` services.md — service-layer uniqueness validation pattern), 2 gotchas (`[SERVG-01]` services.md — `.one_or_none()` vs `.order_by().first()` for unconstrained invariants; `[DBG-01]` db.md — `rolenum` Postgres enum labels are uppercase), 1 foundation gap (stack.yaml `dev_runbook.subprojects[].run_targets`/`test_commands`/`auth` filled in from live discovery — previously empty), 1 decision candidate (`D001` — deferred DB-level UNIQUE constraint on `miembros(casa_id, usuario_id) WHERE activo`, non-blocking). 0 stale references, 0 foundation-deviation reconciliations, 0 CLAUDE.md patches, 0 skill candidates, 0 deprecations, 0 architecture-fact writes (architecture.md has no managed block yet — this fix also didn't change anything architecturally core), 1 Observations note already recorded by verify, 0 no-action items outstanding — everything read in Phase 1 (Judgment's 2 entries, Observations' 1 note, the 3 referenced domain files, stack.yaml, security.yaml, design-principles.yaml, code-practice.yml) resolved to exactly one outcome.
