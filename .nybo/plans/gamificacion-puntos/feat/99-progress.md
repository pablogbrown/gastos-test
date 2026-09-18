# Progress — gamificacion-puntos

## Checklist

### Tasks
- [x] T1 — Niveles, rachas y ranking por mes
- [x] T2 — Logros
- [ ] T3 — Meta de puntos mensual de la casa
- [ ] T4 — Frontend (Ranking, Miembros, Inicio)

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Niveles cruzando cada umbral
- [ ] `[TC-002]` *[INTEGRATION]* — Racha consecutiva se acumula
- [ ] `[TC-003]` *[INTEGRATION]* — Un día sin actividad corta la racha
- [ ] `[TC-004]` *[INTEGRATION]* — Ranking por mes vs. histórico sin regresión
- [ ] `[TC-005]` *[INTEGRATION]* — Logros se desbloquean una sola vez
- [ ] `[TC-006]` *[INTEGRATION]* — Meta de la casa: solo admin, progreso correcto
- [ ] `[TC-007]` *[UNIT]* — Ranking muestra mes/nivel/racha/logros
- [ ] `[TC-008]` *[UNIT]* — Inicio muestra meta; Miembros permite editarla

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-18 | plan | — | — | Spec creada — 4 tareas, 8 test cases. Niveles, rachas, ranking por mes, logros y meta de la casa, todo derivado de `HistorialTarea` ya existente. |
