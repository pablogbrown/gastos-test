# Progress — Membresía duplicada crashea la resolución de actor

## Checklist

### Tasks
- [x] T1 — Validar membresía única por Usuario en `agregar_miembro`
- [x] T2 — Endurecer `resolver_actor_en_casa` contra duplicados preexistentes

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

- [x] **Outcome smoke test**

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Agregar dos veces el mismo Usuario a la misma casa es rechazado con 400
- [x] `[TC-002]` *[INTEGRATION]* — Agregar el mismo Usuario a casas distintas sigue funcionando (control)
- [x] `[TC-003]` *[INTEGRATION]* — Duplicado preexistente en la base no crashea el request (sin 500)
- [x] `[TC-004]` *[INTEGRATION]* — Resolución de actor con duplicados es repetible/determinística

#### Outcome Smoke Test
**Latest:** observed — screen: n/a — outcome not visual · API: observed — POST /auth/registro+login, POST /casas, POST /casas/{id}/miembros (dup rejected 400), duplicate seeded directly in Postgres, PATCH deactivar-admin repeated 5x (403 every time, reproducing the original incident), GET listado repeated 5x (200 every time, never 500), backend logs grepped clean of 500/Traceback/MultipleResultsFound. Driven against the live dockerized dev environment (`docker ps`: db/backend/frontend up).

## Completion Summary
T1 and T2 implemented in `src/services/miembro_service.py` exactly per
task-file contracts. New test file
`tests/integration/api/miembro_membresia_unica.test.py` covers TC-001
through TC-004 (RED confirmed before implementation, GREEN after). Full
suite: 191 passed (134 backend + 57 frontend), zero regressions. Spec-level
verify pass: verified, live evidence observed against the real dockerized
environment, including a direct reproduction of the original authorization
incident (member-attempts-to-deactivate-admin) now resolving 403 every
time.

## Decisions
- [ ] `[D001]` — Add a DB-level UNIQUE constraint on `miembros(casa_id, usuario_id) WHERE activo` as defense-in-depth on top of T1's service-layer check? Deferred, non-blocking — recommendation: leave as-is (see `evidence/decisions.yaml`).

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-14 | plan | — | — | Spec created — 2 tasks (exceeds fix-mode's 1-task default, documented in status.yaml exceptions), 4 test cases, from a critical bug found via manual QA. |
| 2 | 2026-09-14 | execute | — | — | T1+T2 implemented via TDD (RED→GREEN). 4/4 test cases green, full suite 134/134 passed. |
| 3 | 2026-09-14 | verify | verified | observed | Spec-level verify: build/tests/coverage/live evidence all gathered. 191/191 tests passed, 4/4 TC proven, live smoke against real docker env confirmed both the 500 fix and the original auth-incident scenario now resolves 403 consistently (5/5). Coverage unavailable — not configured (pre-existing project decision). |
| 4 | 2026-09-14 | curate | — | — | Curated 5 findings: 1 convention + 2 gotchas (services.md, db.md), 1 foundation gap filled (stack.yaml dev_runbook), 1 decision candidate deferred (D001, non-blocking). |
