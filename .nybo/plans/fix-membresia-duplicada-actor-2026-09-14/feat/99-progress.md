# Progress — Membresía duplicada crashea la resolución de actor

## Checklist

### Tasks
- [ ] T1 — Validar membresía única por Usuario en `agregar_miembro`
- [ ] T2 — Endurecer `resolver_actor_en_casa` contra duplicados preexistentes

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Agregar dos veces el mismo Usuario a la misma casa es rechazado con 400
- [ ] `[TC-002]` *[INTEGRATION]* — Agregar el mismo Usuario a casas distintas sigue funcionando (control)
- [ ] `[TC-003]` *[INTEGRATION]* — Duplicado preexistente en la base no crashea el request (sin 500)
- [ ] `[TC-004]` *[INTEGRATION]* — Resolución de actor con duplicados es repetible/determinística

## Completion Summary
Not yet started.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-14 | plan | — | — | Spec created — 2 tasks (exceeds fix-mode's 1-task default, documented in status.yaml exceptions), 4 test cases, from a critical bug found via manual QA. |
