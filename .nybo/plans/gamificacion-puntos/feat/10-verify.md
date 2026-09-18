# Verify — gamificacion-puntos

## T1 — Niveles, rachas, ranking por mes

### Test Scenarios
- Niveles cruzando cada umbral (TC-001). Racha consecutiva y su corte
  (TC-002/TC-003). Ranking filtrado por mes vs. sin filtro (TC-004).

### Gate Criteria
- `[AUTO]` TC-001 a TC-004 en verde.
- `[AUTO]` Suite completa de `dashboard_service` sin regresión (llama
  a `calcular_ranking` sin `mes`).

## T2 — Logros

### Gate Criteria
- `[AUTO]` TC-005 en verde.
- `[AUTO]` Migración `0020_gamificacion` idempotente contra Postgres
  real.
- `[AUTO]` `completar_tarea` sin regresión para el caso sin logros
  nuevos.

## T3 — Meta de la casa

### Gate Criteria
- `[AUTO]` TC-006 en verde.
- `[AUTO]` `dashboard_service` sin regresión para una casa sin meta
  configurada (`meta_casa: None`).

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-007/TC-008 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `docker compose exec backend python -m pytest tests/` y `npm run
   test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual: completar varias tareas en días distintos para un
   mismo miembro → sube de nivel al cruzar 50 puntos, la racha se
   refleja en Ranking, se desbloquean los logros correspondientes; un
   Administrador configura una meta mensual → Inicio muestra la barra
   de progreso.

## Failure Triage

| If TC-XXX falla | Revisar primero | Patrón de causa raíz |
|---|---|---|
| TC-002/TC-003 | ¿`calcular_racha` cuenta DÍAS distintos o filas de `HistorialTarea`? | Completar 2 tareas el mismo día no debe sumar 2 al conteo de días |
| TC-004 | ¿`dashboard_service.armar_dashboard` sigue llamando `calcular_ranking(casa_id)` sin `mes`? | Un default mal puesto rompe el "últimos 10"/ranking histórico del dashboard |
| TC-005 | ¿`evaluar_logros` chequea si el `LogroObtenido` ya existe ANTES de insertar? | Completar tareas repetidas duplicaría el mismo logro sin el chequeo |
| TC-006 | ¿`calcular_progreso_meta` suma TODOS los miembros del mes, o solo uno? | Confundir "meta de la casa" con "meta de un miembro" |
