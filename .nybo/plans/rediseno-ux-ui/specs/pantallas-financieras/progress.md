# Pantallas financieras - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [ ] T1 — Gastos + Balance
- [ ] T2 — Tarjetas + Suscripciones
- [ ] T3 — Préstamos
- [ ] T4 — Mantenimiento + Mantenimiento Autos

### Verify
- [ ] Verificación (spec-level, una sola pasada tras completar T1–T4)

### Curate
- [ ] Curación de hallazgos post-verify

#### Test Cases
- [ ] `[TC-001]` *[UNIT]* — chips de estado en Gastos usan colores semánticos del tema.
- [ ] `[TC-002]` *[UNIT]* — un préstamo "Rechazado" usa `palette.error` igual que en las otras pantallas.
- [ ] `[TC-003]` *[UNIT]* — sin tarjetas registradas, se muestra `EmptyState`.
- [ ] `[TC-004]` *[UNIT]* — un mes sin gastos muestra `EmptyState` en vez de tabla vacía.
- [ ] `[TC-005]` *[UNIT]* — Suscripciones usa `PageHeader` con acción de alta funcional.
- [ ] `[TC-006]` *[INTEGRATION]* — los 7 test suites existentes pasan sin modificar sus queries.

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| — | — | Not yet started. | not started |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 4 tasks, 6 test cases. |
