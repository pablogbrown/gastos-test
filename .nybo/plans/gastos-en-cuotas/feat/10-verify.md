# Verify — Registrar un gasto en cuotas

## T1 — Columnas de cuota

### Gate Criteria
- `[AUTO]` Suite completa en verde con el modelo actualizado.
- `[AUTO]` Migración idempotente contra Postgres real (base temporal).

## T2 — `registrar_gasto` genera N gastos

### Test Scenarios
- 3 cuotas de un monto exacto → fechas consecutivas mes a mes (TC-001).
- Monto no divisible exacto entre cuotas → redondeo ajustado en la última (TC-002).
- Las 3 filas comparten grupo y tienen número/total correctos (TC-003).
- Sin `cuotas` → comportamiento idéntico a hoy (TC-004).
- `cuotas=0` → rechazado (TC-005).
- Integración con balance mensual: cuota de hoy vs. cuota futura (TC-006).

### Gate Criteria
- `[AUTO]` TC-001 a TC-006 en verde.

## T3 — API expone `cuotas`

### Gate Criteria
- `[AUTO]` `pytest tests/` completo sigue en verde.

## T4 — Frontend ofrece cuotas

### Gate Criteria
- `[AUTO]` TC-007 en verde.
- `[AUTO]` `npm run build` sin errores de tipos.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra el docker-compose local: cargar un gasto real en
   3 cuotas desde la UI → aparecen 3 gastos en el historial, con fechas
   correctas; el balance de este mes solo refleja la primera.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001 | ¿`_sumar_meses` maneja el cambio de año (dic → ene)? | Cálculo de mes/año sin el `//`/`%` correcto |
| TC-002 | ¿Se reutiliza `_dividir_importe` tal cual, o se reimplementó el redondeo? | Una reimplementación nueva puede no coincidir con el criterio ya probado |
| TC-004 | ¿La rama `cuotas is None` realmente reproduce el camino de código anterior sin ninguna diferencia? | Alguna validación nueva (ej. de `cuotas`) se ejecuta incluso cuando `cuotas` es `None` |
| TC-006 | ¿`balance-mensual` (T1 de esa spec) ya está mergeada en la rama base de este build? | Esta spec depende de esa — si se construye antes, `calcular_balance` todavía no acepta `mes` |
