# Verify — Balance filtrable por mes

## T1 — `calcular_balance` filtra por mes

### Test Scenarios
- Sin `mes` → usa el mes calendario actual (TC-001).
- Con `mes="YYYY-MM"` explícito → solo ese mes (TC-002).
- Formato de `mes` inválido → `ValidationError` (TC-003, verificado también en T2 como 400 HTTP).

### Gate Criteria
- `[AUTO]` TC-001, TC-002, TC-003 en verde.
- `[AUTO]` `pytest tests/` completo sigue en verde — ningún llamador existente de `calcular_balance` (dashboard_service) se rompe por el nuevo parámetro opcional.

## T2 — Ruta y cliente

### Gate Criteria
- `[AUTO]` `GET /casas/{id}/balance?mes=invalido` responde 400.
- `[AUTO]` `npm run build` sin errores de tipos.

## T3 — Selector de mes

### Gate Criteria
- `[AUTO]` TC-004, TC-005 en verde.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra el docker-compose local: registrar un gasto con
   fecha de un mes futuro (posible manualmente via API aunque la UI de
   Gastos todavía no ofrezca cuotas) → el Balance del mes actual NO lo
   refleja; cambiando el selector al mes futuro correspondiente, sí
   aparece.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001/002 | ¿El filtro `Gasto.fecha.between(desde, hasta)` se aplica a AMBAS queries (pagos y correspondientes)? | Filtro aplicado solo a una de las dos, descompensando pago vs. correspondía |
| TC-003 | ¿`_rango_mes` valida el rango de mes (1-12), no solo que sean enteros? | `"2026-13"` pasaría el `int()` pero no es un mes válido |
| TC-004/005 | ¿El `useEffect` de `cargar()` incluye `mes` en sus dependencias? | Cambiar el selector actualiza el estado pero no dispara un nuevo fetch |
