# Pantallas de casa - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [x] T1 — Miembros como tarjetas de perfil
- [x] T2 — Ranking con progreso visual
- [x] T3 — Tareas con estado visual claro
- [x] T4 — Actividad como feed cronológico

### Verify
- [x] Verificación (spec-level, una sola pasada tras completar T1–T4)

### Curate
- [x] Curación de hallazgos post-verify

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — cada miembro es una tarjeta con avatar/nombre/chip de rol.
- [x] `[TC-002]` *[UNIT]* — un miembro "Pendiente" tiene un chip visualmente distinto.
- [x] `[TC-003]` *[UNIT]* — el progreso de nivel se muestra con un indicador visual.
- [x] `[TC-004]` *[UNIT]* — los logros se muestran como chips distintos entre sí.
- [x] `[TC-005]` *[UNIT]* — tareas completada/pendiente son distinguibles por color/ícono.
- [x] `[TC-006]` *[UNIT]* — cada tipo de evento en Actividad usa un ícono distinto.
- [x] `[TC-007]` *[INTEGRATION]* — los 4 test suites existentes pasan (3 queries estructurales ajustadas, ver Judgment J001 — nunca una query de rol/label).

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| 1 | 2026-09-23 | Build/lint/tests verdes (168/168, 25 archivos, 0 regresión funcional). | resolved |
| 2 | 2026-09-23 | Coverage no disponible (sin proveedor instalado) — decision class `new-dependency`, diferida a un humano. Ver `decisions.yaml` D001. | open |
| 3 | 2026-09-23 | Live evidence capturada vía Playwright (Chrome del sistema) contra un dev server aislado de este worktree: Miembros/Ranking/Tareas/Actividad confirmados con datos reales (miembro pendiente, tarea completada de 60 puntos). Ver `evidence/1/screenshots/`. | resolved |
| 4 | 2026-09-23 | "Meta de la casa" en Ranking (sugerida por el task file de T2) no implementada — ningún REQ/TC la exige y requeriría un fetch nuevo. Ver Judgment J002 / `suggestions.yaml` S002. | open |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 4 tasks, 7 test cases. |
| 2 | 2026-09-23 | build | ready | live (Playwright, desktop) | T1–T4 implementados, 168/168 tests verdes, 0 regresión funcional. Coverage diferido (new-dependency, D001). "Meta de la casa" en Ranking omitida (J002). |
