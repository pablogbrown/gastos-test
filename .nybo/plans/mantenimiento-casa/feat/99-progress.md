# Progress — Mantenimiento de la casa

## Checklist

### Tasks
- [x] T1 — `ItemMantenimiento` + `MaterialMantenimiento`; migración
- [x] T2 — `mantenimiento_service` (alta/materiales/completar/alerta)
- [x] T3 — Rutas; dashboard expone la alerta
- [x] T4 — Pantalla "Mantenimiento"; banner en Inicio; nav agrupada con Tareas

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Alta de ítem con datos válidos
- [x] `[TC-002]` *[INTEGRATION]* — Recurrente sin periodicidad/fecha rechazado
- [x] `[TC-003]` *[INTEGRATION]* — Materiales persisten con conseguido=false
- [x] `[TC-004]` *[INTEGRATION]* — Marcar material como conseguido
- [x] `[TC-005]` *[INTEGRATION]* — Completar no-recurrente sin nueva instancia
- [x] `[TC-006]` *[INTEGRATION]* — Completar recurrente genera la siguiente
- [x] `[TC-007]` *[INTEGRATION]* — Completar antes de tiempo rechazado
- [x] `[TC-008]` *[UNIT]* — Alerta a 5 días sí, a 20 días no
- [x] `[TC-009]` *[UNIT]* — Formulario crea ítem con materiales
- [x] `[TC-010]` *[UNIT]* — Banner de alerta en Inicio

## Completion Summary
Las 4 tareas implementadas end-to-end: modelo + migración `0017`
idempotente contra Postgres real, `mantenimiento_service` con alta,
materiales, completar (gate de recurrencia + generación de siguiente
instancia) y alerta, rutas HTTP + `mantenimientoConAlerta` en el
dashboard, y la pantalla "Mantenimiento" + banner en Inicio + nav
agrupada. TC-001 a TC-010 pasan. Suite completa: 328 pytest (1 skip
esperado, requiere `DATABASE_URL` externo) + 120 vitest, `npm run
build`/`lint` sin errores. Smoke manual contra `docker-compose` (Postgres
real): alta con materiales, banner de alerta a 5 días, completar antes
de tiempo rechazado con 409, completar en fecha genera la siguiente
instancia con la fecha correcta, no completable el mismo día.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 10 test cases. Foundation para `mantenimiento-autos` (build en ese orden). |
| 2 | 2026-09-16 | build | ready | pass | 4 tareas implementadas, TC-001 a TC-010 en verde, smoke en vivo contra Postgres real vía docker-compose. |
