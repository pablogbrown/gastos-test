# Verify — Estado de pago de un gasto

## T1 — Columna `estado`

### Gate Criteria
- `[AUTO]` Suite completa en verde con el modelo actualizado.
- `[AUTO]` Migración idempotente contra Postgres real.

## T2 — Servicios propagan `estado`

### Test Scenarios
- Sin `estado` → default "pagado" (TC-001). Con `estado="a_pagar"` → persiste (TC-002).
- 3 cuotas heredan el mismo `estado` (TC-003).
- Gasto generado por suscripción nace "a_pagar" (TC-004).
- Gastos generados al importar un resumen nacen "a_pagar" (TC-005).
- `actualizar_estado_gasto` cambia el estado en ambos sentidos (TC-006).
- Cambiar el estado no altera `calcular_balance` (TC-008).

### Gate Criteria
- `[AUTO]` TC-001 a TC-006 y TC-008 en verde.

## T3 — API

### Gate Criteria
- `[AUTO]` TC-007 en verde (estado inválido → 400).
- `[AUTO]` `pytest tests/` completo sigue en verde.

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-009 y TC-010 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra docker-compose: importar un resumen → los gastos
   creados aparecen "A pagar"; clic en el chip los pasa a "Pagado"; el
   Balance del mes no cambia antes/después.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-004/TC-005 | ¿Cada call-site de `registrar_gasto` en `suscripcion_service.py`/`resumen_importer_service.py` pasa `estado="a_pagar"` explícitamente? | Olvidar uno de los 3 call-sites de `resumen_importer_service.py` (normal, cuotas restantes, suscripción detectada) |
| TC-008 | ¿Se tocó `balance_service.py` en esta spec? | No debería haber ningún cambio ahí — si el test falla, revisar que no se haya filtrado por `estado` sin querer |
