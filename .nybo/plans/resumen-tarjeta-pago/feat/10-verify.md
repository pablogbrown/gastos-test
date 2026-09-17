# Verify — resumen-tarjeta-pago

## T1 — Modelo + migración

### Gate Criteria
- `[AUTO]` Suite completa en verde con los modelos actualizados.
- `[AUTO]` Migración `0019_resumen_tarjeta` idempotente contra Postgres
  real (corrida dos veces seguidas no lanza excepción).

## T2 — Service tracking

### Test Scenarios
- Importar un resumen crea `ResumenTarjeta` correctamente (TC-001).
- Importar el mismo PDF dos veces rechaza la segunda sin crear gastos
  (TC-002).
- Cada gasto creado (directo/cuota/suscripción) queda vinculado al
  resumen correcto (TC-003).
- Pagar un resumen marca todos sus gastos y el resumen como pagados
  (TC-004), sin afectar otros resúmenes/tarjetas ni permitir pagar dos
  veces el mismo (TC-005).
- Listar resúmenes de una tarjeta devuelve todos, más reciente primero
  (TC-006).

### Gate Criteria
- `[AUTO]` TC-001 a TC-006 en verde.
- `[AUTO]` `resumen_importer.test.py` (test preexistente) sigue en
  verde sin modificaciones.

## T3 — API

### Gate Criteria
- `[AUTO]` `pytest tests/` completo sigue en verde.
- `[AUTO]` Importar duplicado responde 409 vía HTTP.

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-007 y TC-008 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual: importar un resumen → aparece en la lista de
   resúmenes de esa tarjeta como "Pendiente"; volver a subir el mismo
   PDF → error claro, sin gastos duplicados; click en "Pagar resumen" →
   todos los gastos de ese resumen pasan a "Pagado" en la pantalla
   Gastos, y el resumen queda "Pagado" en Tarjetas.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-002 | ¿El chequeo de duplicado corre ANTES de `actualizar_tarjeta`? | Si corre después, la tarjeta ya quedó modificada aunque se rechace el resto |
| TC-003 | ¿Las 3 rutas de creación de gasto (directo/cuota/suscripción) reciben `resumen_id`? | Fácil olvidar la rama de `registrar_suscripcion_detectada` |
| TC-004/005 | ¿`pagar_resumen` filtra por `resumen_id`, no por `tarjeta_id`? | Un filtro por tarjeta pagaría gastos de otros resúmenes de la misma tarjeta |
