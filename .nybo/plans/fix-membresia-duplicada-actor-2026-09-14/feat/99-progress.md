# Progress — Membresía duplicada crashea la resolución de actor

## Checklist

### Tasks
- [x] T1 — Validar membresía única por Usuario en `agregar_miembro`
- [x] T2 — Endurecer `resolver_actor_en_casa` contra duplicados preexistentes

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Agregar dos veces el mismo Usuario a la misma casa es rechazado con 400
- [x] `[TC-002]` *[INTEGRATION]* — Agregar el mismo Usuario a casas distintas sigue funcionando (control)
- [x] `[TC-003]` *[INTEGRATION]* — Duplicado preexistente en la base no crashea el request (sin 500)
- [x] `[TC-004]` *[INTEGRATION]* — Resolución de actor con duplicados es repetible/determinística

## Completion Summary
T1 and T2 implemented in `src/services/miembro_service.py` exactly per
task-file contracts. New test file
`tests/integration/api/miembro_membresia_unica.test.py` covers TC-001
through TC-004 (RED confirmed before implementation, GREEN after). Full
suite: 134 passed (130 baseline + 4 new), zero regressions.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-14 | plan | — | — | Spec created — 2 tasks (exceeds fix-mode's 1-task default, documented in status.yaml exceptions), 4 test cases, from a critical bug found via manual QA. |
| 2 | 2026-09-14 | execute | — | — | T1+T2 implemented via TDD (RED→GREEN). 4/4 test cases green, full suite 134/134 passed. |
