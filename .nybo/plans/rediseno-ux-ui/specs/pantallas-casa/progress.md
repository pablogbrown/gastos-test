# Pantallas de casa - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [ ] T1 — Miembros como tarjetas de perfil
- [ ] T2 — Ranking con progreso visual
- [ ] T3 — Tareas con estado visual claro
- [ ] T4 — Actividad como feed cronológico

### Verify
- [ ] Verificación (spec-level, una sola pasada tras completar T1–T4)

### Curate
- [ ] Curación de hallazgos post-verify

#### Test Cases
- [ ] `[TC-001]` *[UNIT]* — cada miembro es una tarjeta con avatar/nombre/chip de rol.
- [ ] `[TC-002]` *[UNIT]* — un miembro "Pendiente" tiene un chip visualmente distinto.
- [ ] `[TC-003]` *[UNIT]* — el progreso de nivel se muestra con un indicador visual.
- [ ] `[TC-004]` *[UNIT]* — los logros se muestran como chips distintos entre sí.
- [ ] `[TC-005]` *[UNIT]* — tareas completada/pendiente son distinguibles por color/ícono.
- [ ] `[TC-006]` *[UNIT]* — cada tipo de evento en Actividad usa un ícono distinto.
- [ ] `[TC-007]` *[INTEGRATION]* — los 4 test suites existentes pasan sin modificar sus queries.

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| — | — | Not yet started. | not started |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 4 tasks, 7 test cases. |
