# Verify — Mantenimiento de autos

## T1 — `Auto`; `auto_id`

### Gate Criteria
- `[AUTO]` Suite completa en verde con los modelos actualizados.
- `[AUTO]` Migración idempotente contra Postgres real.

## T2 — `auto_service` + `mantenimiento_service`

### Test Scenarios
- Alta de auto válida (TC-001). Item con `auto_id` queda asociado (TC-002).
- Listado sin filtro = solo casa; con filtro = solo ese auto (TC-003).
- Alerta incluye ítems de auto (TC-004). Auto de otra casa → 404 (TC-005).

### Gate Criteria
- `[AUTO]` TC-001 a TC-005 en verde.

## T3 — API

### Gate Criteria
- `[AUTO]` `pytest tests/` completo sigue en verde.

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-006 y TC-007 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual: registrar un auto, cargarle un service con fecha
   próxima → aparece en "Mantenimiento Autos" y en el banner de Inicio;
   "Mantenimiento" (de la casa) sigue mostrando solo sus propios ítems.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-003 | ¿`listar_items` sin `auto_id` filtra `IS NULL`, o sigue devolviendo todo como en `mantenimiento-casa`? | Olvidar actualizar el default tras agregar la columna |
| TC-007 | ¿`Mantenimiento.tsx` sigue llamando a `listarItems(casaId)` sin `autoId`? | Confirmar que no se tocó su código en esta spec, solo el cliente/tipo compartido |
