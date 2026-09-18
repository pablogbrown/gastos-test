# Progress — gamificacion-puntos

## Checklist

### Tasks
- [x] T1 — Niveles, rachas y ranking por mes
- [x] T2 — Logros
- [x] T3 — Meta de puntos mensual de la casa
- [x] T4 — Frontend (Ranking, Miembros, Inicio)

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Niveles cruzando cada umbral
- [x] `[TC-002]` *[INTEGRATION]* — Racha consecutiva se acumula
- [x] `[TC-003]` *[INTEGRATION]* — Un día sin actividad corta la racha
- [x] `[TC-004]` *[INTEGRATION]* — Ranking por mes vs. histórico sin regresión
- [x] `[TC-005]` *[INTEGRATION]* — Logros se desbloquean una sola vez
- [x] `[TC-006]` *[INTEGRATION]* — Meta de la casa: solo admin, progreso correcto
- [x] `[TC-007]` *[UNIT]* — Ranking muestra mes/nivel/racha/logros
- [x] `[TC-008]` *[UNIT]* — Inicio muestra meta; Miembros permite editarla

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-18 | plan | — | — | Spec creada — 4 tareas, 8 test cases. Niveles, rachas, ranking por mes, logros y meta de la casa, todo derivado de `HistorialTarea` ya existente. |
| 2 | 2026-09-18 | build | ready | live (API) | T1-T4 implementados vía TDD (RED→GREEN→REFACTOR). 388 tests backend + 150 frontend en verde (5 fallas pre-existentes de `capacitor_config.test.py` excluidas, confirmadas en el commit base). Migración `0020_gamificacion` verificada idempotente contra Postgres real. Smoke live contra el stack corriendo: nivel/racha/logros/ranking-por-mes/meta-de-casa confirmados end-to-end vía API real. Curate diferido a pedido explícito del usuario. |
