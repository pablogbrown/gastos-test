# Verify — Suscripciones mensuales de gastos

## T1 — Modelo `Suscripcion`

### Gate Criteria
- `[AUTO]` Suite completa en verde con el modelo nuevo.
- `[AUTO]` Migración idempotente contra Postgres real (base temporal).

## T2 — Servicio de suscripciones

### Test Scenarios
- Crear suscripción → gasto del mes actual generado de inmediato (TC-001).
- Listar gastos con una pendiente del mes pasado → se genera la de este mes (TC-002).
- Listar gastos dos veces en el mismo mes → no duplica (TC-003).
- Cancelar → no genera más, lo ya generado queda intacto (TC-004).
- Un `member` no puede crear ni cancelar (TC-005).

### Gate Criteria
- `[AUTO]` TC-001 a TC-005 en verde.
- `[AUTO]` Ningún test existente de `gastos`/`dashboard` cambia de resultado cuando la casa no tiene ninguna suscripción.

## T3 — Rutas HTTP

### Gate Criteria
- `[AUTO]` `pytest tests/` completo sigue en verde.

## T4 — Pantalla + creación desde Gastos

### Gate Criteria
- `[AUTO]` TC-006, TC-007 en verde.
- `[AUTO]` `npm run build` sin errores de tipos.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra el docker-compose local: crear una suscripción
   real desde la UI → aparece el gasto de este mes; entrar a
   Suscripciones → aparece listada y activa; cancelarla → pasa a
   inactiva sin borrar el gasto ya generado.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001 | ¿`crear_suscripcion` llama a `registrar_gasto` ANTES o DESPUÉS de comprometer la fila `Suscripcion`? | Orden invertido puede dejar un gasto huérfano sin `suscripcion_id` válido si algo falla en el medio |
| TC-002/003 | ¿La comparación de mes usa el mismo formato `YYYY-MM` en ambos lados (`ultimo_mes_generado` guardado vs. mes actual calculado)? | Comparar un `date` contra un `str`, o formatos de mes distintos (`9` vs `09`) |
| TC-004 | ¿`cancelar_suscripcion` toca algún `Gasto` ya generado? | No debería tocar ninguno — si un test falla acá, revisar que no se agregó un `cascade` o un update accidental |
| TC-005 | ¿`crear_suscripcion`/`cancelar_suscripcion` llaman al mismo chequeo de admin que `miembro_service`? | Chequeo de rol omitido o mal importado |
