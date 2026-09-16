# Progress — Mantenimiento de autos

## Checklist

### Tasks
- [x] T1 — `Auto`; `ItemMantenimiento.auto_id`; migración
- [x] T2 — `auto_service`; `mantenimiento_service` filtra por auto
- [x] T3 — Rutas de autos; mantenimiento acepta `auto_id`
- [x] T4 — Pantalla "Mantenimiento Autos"; nav

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Alta de auto con datos válidos
- [x] `[TC-002]` *[INTEGRATION]* — Item con auto_id queda asociado
- [x] `[TC-003]` *[INTEGRATION]* — Listado filtra por auto correctamente
- [x] `[TC-004]` *[INTEGRATION]* — Alerta incluye ítems de auto
- [x] `[TC-005]` *[INTEGRATION]* — Auto de otra casa rechazado (404)
- [x] `[TC-006]` *[UNIT]* — Pantalla agrupa auto + sus ítems
- [x] `[TC-007]` *[UNIT]* — Mantenimiento de la casa sin regresión

## Completion Summary
Las 4 tareas implementadas y verificadas en un solo ciclo. Merge previo
de `main` (mantenimiento-casa) limpio, sin conflictos. Backend 349/349,
frontend 123/123, build y lint limpios. Las 7 test cases confirmadas
tanto por test automatizado como por smoke en vivo (API real + browser
real contra el entorno dockerizado ya levantado). Sin decisiones
abiertas — ver `evidence/1/build-results.md` para el detalle de
Judgment (estrategia de FK de `auto_id`, y la exclusión del fallo
preexistente de Node/Docker en el frontend).

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 7 test cases. Depende de `mantenimiento-casa` (build en ese orden — necesita `ItemMantenimiento` ya mergeado). |
| 2 | 2026-09-16 | build | verified | pass | Merge de `main` limpio, T1-T4 implementadas en un ciclo, 349+123 tests verdes, TC-001 a TC-007 confirmadas en vivo (API + browser). |
