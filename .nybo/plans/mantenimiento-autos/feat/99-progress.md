# Progress — Mantenimiento de autos

## Checklist

### Tasks
- [ ] T1 — `Auto`; `ItemMantenimiento.auto_id`; migración
- [ ] T2 — `auto_service`; `mantenimiento_service` filtra por auto
- [ ] T3 — Rutas de autos; mantenimiento acepta `auto_id`
- [ ] T4 — Pantalla "Mantenimiento Autos"; nav

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Alta de auto con datos válidos
- [ ] `[TC-002]` *[INTEGRATION]* — Item con auto_id queda asociado
- [ ] `[TC-003]` *[INTEGRATION]* — Listado filtra por auto correctamente
- [ ] `[TC-004]` *[INTEGRATION]* — Alerta incluye ítems de auto
- [ ] `[TC-005]` *[INTEGRATION]* — Auto de otra casa rechazado (404)
- [ ] `[TC-006]` *[UNIT]* — Pantalla agrupa auto + sus ítems
- [ ] `[TC-007]` *[UNIT]* — Mantenimiento de la casa sin regresión

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 7 test cases. Depende de `mantenimiento-casa` (build en ese orden — necesita `ItemMantenimiento` ya mergeado). |
