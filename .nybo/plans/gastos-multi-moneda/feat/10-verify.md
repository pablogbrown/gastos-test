# Verify — Multi-moneda en gastos, cuotas y suscripciones

## T1 — Columna `moneda`

### Gate Criteria
- `[AUTO]` Suite completa en verde con los modelos actualizados.
- `[AUTO]` Migración idempotente contra Postgres real (base temporal).

## T2 — Servicios propagan y separan por moneda

### Test Scenarios
- Gasto con `moneda="USD"` persiste correctamente (TC-001).
- Gasto sin `moneda` → default ARS, sin cambios de comportamiento (TC-002).
- Casa con actividad en ambas monedas el mismo mes → filas separadas (TC-003).
- Mes sin actividad en USD → ninguna fila USD (TC-004).
- Deudores/acreedores en ambas monedas → transferencias nunca cruzan moneda (TC-005).
- Suscripción en USD → gasto generado hereda USD (TC-006).
- Gasto en 3 cuotas con USD → las 3 cuotas en USD (TC-007).

### Gate Criteria
- `[AUTO]` TC-001 a TC-007 en verde.

## T3 — API expone `moneda`

### Gate Criteria
- `[AUTO]` TC-008 en verde (moneda inválida → 400).
- `[AUTO]` `pytest tests/` completo sigue en verde.

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-009 y TC-010 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra docker-compose: registrar un gasto en USD y otro
   en ARS el mismo mes → la pantalla Balance muestra dos secciones
   separadas, cada una con su propio total y transferencias sugeridas.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-004 | ¿Se está agregando una fila USD en 0 para todo miembro, en vez de solo los que tuvieron actividad? | Copiar el criterio actual de ARS (todos, incluso en 0) también para USD |
| TC-005 | ¿`sugerir_transferencias` agrupa por moneda antes de correr el greedy, o corre el greedy sobre la lista completa? | Olvidar el `groupby` antes de emparejar deudores/acreedores |
| TC-006 | ¿`generar_gastos_pendientes` pasa `moneda=suscripcion.moneda` a `registrar_gasto`, o deja el default? | Import diferido de `registrar_gasto` (patrón ya usado) sin pasar el nuevo parámetro |
| TC-007 | ¿`_crear_gastos_en_cuotas` recibe `moneda` como parámetro y lo asigna a cada cuota? | Cuota creada con el default en vez de heredar la moneda del gasto original |
