# Progress — Gestión de Tareas y Puntos

## Checklist

### Tasks
- [ ] T1 — Data Layer: Tarea e Historial
- [ ] T2 — Service Layer: Tareas, Puntos y Ranking
- [ ] T3 — API Routes: Tareas y Ranking
- [ ] T4 — UI: Tareas, Ranking e Historial

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[UNIT]* — Crear tarea con nombre y puntos válidos
- [ ] `[TC-002]` *[UNIT]* — Crear tarea sin nombre es rechazado
- [ ] `[TC-003]` *[UNIT]* — Tarea nueva queda en estado Pendiente
- [ ] `[TC-004]` *[UNIT]* — Tarea sin responsable puede completarla cualquier miembro
- [ ] `[TC-005]` *[UNIT]* — Completar tarea registra quién, cuándo y otorga puntos
- [ ] `[TC-006]` *[UNIT]* — No se otorgan puntos dos veces por la misma finalización
- [ ] `[TC-007]` *[UNIT]* — Puntos acumulados de un miembro se calculan correctamente
- [ ] `[TC-008]` *[UNIT]* — Ranking ordenado de mayor a menor puntaje
- [ ] `[TC-009]` *[INTEGRATION]* — Tarea recurrente genera nueva instancia al completarse
- [ ] `[TC-010]` *[INTEGRATION]* — Historial conserva registros de miembros desactivados

## Completion Summary
Not yet started.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 10 test cases. |
