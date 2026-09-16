# Verify — Vista mensual del listado de Gastos

## T1 — `listar_gastos` acepta `mes`

### Test Scenarios
- Con `mes="2026-09"` → solo gastos de septiembre (TC-001).
- Sin `mes` → todos los gastos, sin cambios (TC-002).
- `armar_dashboard` sigue viendo el historial completo (TC-006, control).

### Gate Criteria
- `[AUTO]` TC-001, TC-002 y TC-006 en verde.

## T2 — API

### Gate Criteria
- `[AUTO]` TC-003 en verde.
- `[AUTO]` `pytest tests/` completo sigue en verde.

## T3 — Frontend

### Gate Criteria
- `[AUTO]` TC-004 y TC-005 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra docker-compose: entrar a Gastos con datos en
   varios meses → el mes actual está preseleccionado y el listado solo
   muestra ese mes; cambiar el selector muestra el mes elegido; Inicio
   sigue mostrando gastos recientes de toda la casa.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-002/TC-006 | ¿`listar_gastos(casa_id)` sin `mes` sigue devolviendo todos los gastos? | Cambiar por error el default de `mes` a "mes actual" en vez de "sin filtro" |
| TC-005 | ¿El estado `mes` se inicializa en el mismo render inicial, no en un `useEffect` posterior? | Mismo patrón ya usado en `Balance.tsx` — copiar tal cual |
