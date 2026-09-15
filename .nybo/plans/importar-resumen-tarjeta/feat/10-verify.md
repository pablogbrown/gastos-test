# Verify — Importar resumen de tarjeta en PDF

## T1 — Parser puro + `Gasto.tarjeta_id`

### Gate Criteria
- `[AUTO]` Parser extrae correctamente cierre/vencimiento/saldo y consumos del PDF de muestra (o fixture equivalente).
- `[AUTO]` Líneas de "Impuestos, cargos e intereses" nunca llegan a `ResumenParseado.consumos` (TC-008).
- `[AUTO]` Un PDF sin los marcadores esperados lanza `PdfFormatoNoReconocidoError` (TC-009).
- `[AUTO]` Migración 0012 idempotente contra Postgres real.

## T2 — `resumen_importer_service`

### Test Scenarios
- Importar actualiza la tarjeta (TC-001).
- Consumo en pesos/dólares crea el gasto en la moneda correcta (TC-002/TC-003).
- "C.04/06" crea exactamente las cuotas restantes (TC-004).
- Comercio reconocido sin suscripción previa + Administrador → crea Suscripcion (TC-005).
- Comercio reconocido con suscripción activa existente → reutiliza, no duplica (TC-006).
- Comercio reconocido + actor no Administrador → gasto suelto, no falla la importación (TC-007).

### Gate Criteria
- `[AUTO]` TC-001 a TC-007 en verde.

## T3 — API

### Gate Criteria
- `[AUTO]` `POST .../resumen` con el PDF de ejemplo responde 200 con los contadores correctos.
- `[AUTO]` TC-009 responde 422.

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-010 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra docker-compose: subir el PDF de ejemplo real
   desde la pantalla Tarjetas → se actualiza el vencimiento de la
   tarjeta, aparecen los gastos nuevos en Gastos/Balance, separados
   correctamente por moneda, con las cuotas y suscripciones vinculadas
   correctamente.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-004 | ¿El rango de cuotas generadas es `cuota_actual..cuota_total` inclusive, o arranca en 1? | Reutilizar por error la lógica de `_crear_gastos_en_cuotas` (siempre arranca en 1) |
| TC-006 | ¿La búsqueda de Suscripcion existente es case-insensitive y filtra por `activa=True`? | Comparación exacta de string, o no filtrar inactivas |
| TC-007 | ¿`registrar_suscripcion_detectada` devuelve `(None, True)` sin lanzar `PermissionDeniedError`? | Reutilizar `_validar_actor_admin` directamente en vez de manejarlo como degradación |
| TC-008 | ¿El parser corta la sección de consumos ANTES de "Impuestos, cargos e intereses", o sigue leyendo? | Regex de fin de sección solo busca "TOTAL CONSUMOS" y no la sección de impuestos |
| TC-009 | ¿Un PDF cualquiera (no resumen) hace que el parser devuelva un `ResumenParseado` vacío en vez de lanzar la excepción? | Falta de validación de que los marcadores de cierre/vencimiento existan |
