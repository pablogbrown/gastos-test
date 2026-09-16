# Progress — Mantenimiento de la casa

## Checklist

### Tasks
- [ ] T1 — `ItemMantenimiento` + `MaterialMantenimiento`; migración
- [ ] T2 — `mantenimiento_service` (alta/materiales/completar/alerta)
- [ ] T3 — Rutas; dashboard expone la alerta
- [ ] T4 — Pantalla "Mantenimiento"; banner en Inicio; nav agrupada con Tareas

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Alta de ítem con datos válidos
- [ ] `[TC-002]` *[INTEGRATION]* — Recurrente sin periodicidad/fecha rechazado
- [ ] `[TC-003]` *[INTEGRATION]* — Materiales persisten con conseguido=false
- [ ] `[TC-004]` *[INTEGRATION]* — Marcar material como conseguido
- [ ] `[TC-005]` *[INTEGRATION]* — Completar no-recurrente sin nueva instancia
- [ ] `[TC-006]` *[INTEGRATION]* — Completar recurrente genera la siguiente
- [ ] `[TC-007]` *[INTEGRATION]* — Completar antes de tiempo rechazado
- [ ] `[TC-008]` *[UNIT]* — Alerta a 5 días sí, a 20 días no
- [ ] `[TC-009]` *[UNIT]* — Formulario crea ítem con materiales
- [ ] `[TC-010]` *[UNIT]* — Banner de alerta en Inicio

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 10 test cases. Foundation para `mantenimiento-autos` (build en ese orden). |
