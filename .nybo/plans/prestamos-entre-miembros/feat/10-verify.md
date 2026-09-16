# Verify — Préstamos entre miembros

## T1 — Modelo `Prestamo`

### Gate Criteria
- `[AUTO]` Suite completa en verde con el modelo nuevo.
- `[AUTO]` Migración idempotente contra Postgres real.

## T2 — `prestamo_service`

### Test Scenarios
- Alta válida → "pendiente" (TC-001). Prestamista == deudor → 400 (TC-002). Moneda inválida → 400 (TC-003).
- Cambio de estado en ambos sentidos (TC-004). Listado ordenado por fecha descendente (TC-005).
- Crear/actualizar un préstamo no cambia `calcular_balance` (TC-006).

### Gate Criteria
- `[AUTO]` TC-001 a TC-006 en verde.

## T3 — API

### Gate Criteria
- `[AUTO]` TC-001 a TC-005 en verde a nivel HTTP.

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-007 y TC-008 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual: registrar un préstamo entre dos miembros → aparece
   "Pendiente"; clic en el chip → pasa a "Pagado"; Balance no cambia en
   ningún momento.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-002 | ¿La validación compara los dos UUIDs, o solo verifica que existan? | Falta el chequeo explícito `prestamista_id != deudor_id` |
| TC-006 | ¿`balance_service.py` fue tocado en esta spec? | No debería — si el test falla, revisar que `crear_prestamo`/`actualizar_estado_prestamo` no toquen `Gasto`/`GastoParticipante` |
