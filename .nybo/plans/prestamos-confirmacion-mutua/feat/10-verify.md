# Verify — Confirmación mutua de un préstamo

## T1 — Columnas de confirmación

### Gate Criteria
- `[AUTO]` Suite completa en verde con el modelo actualizado.
- `[AUTO]` Migración idempotente contra Postgres real.

## T2 — `confirmar_prestamo` + guard

### Test Scenarios
- Prestamista registra → su rol confirmado, deudor pendiente (TC-001). Deudor registra → inverso (TC-002). Tercero registra → ambos pendientes (TC-003).
- Un tercero intenta confirmar → 403 (TC-004, a nivel servicio: PermissionDeniedError).
- La parte pendiente confirma → con ambos true, estado_confirmacion="confirmado" (TC-005).
- La parte pendiente rechaza → "rechazado" permanente (TC-006).
- Cambiar pagado/pendiente antes de confirmar → rechazado (TC-007).

### Gate Criteria
- `[AUTO]` TC-001 a TC-007 en verde.

## T3 — API

### Gate Criteria
- `[AUTO]` TC-004, TC-005, TC-006, TC-007 en verde a nivel HTTP (403/400 correctos).

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-008 y TC-009 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra docker-compose: registrar un préstamo con dos
   usuarios distintos logueados (o simulando el cambio de sesión) →
   confirmar/rechazar refleja correctamente el nuevo estado; intentar
   marcar "pagado" antes de confirmar falla.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-003 | ¿`crear_prestamo` compara `actor` contra `prestamista_id`/`deudor_id` antes de fijar los booleanos, o los deja en `True` por default? | Olvidar el caso "actor es un tercero" |
| TC-006 | ¿`estado_confirmacion` devuelve "rechazado" apenas UNO de los dos es `False`, sin esperar al otro? | Condición mal ordenada (revisar primero "ambos true" en vez de "alguno false") |
| TC-009 | ¿La condición "me toca confirmar" compara `miembroIdActual` contra el rol correcto Y que ese rol siga en `null`? | Mostrar los botones a la parte que ya confirmó, o a la que ya fue rechazada |
