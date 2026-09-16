# Verify — Gastos sin reparto entre participantes

## T1 — Elimina `GastoParticipante`

### Gate Criteria
- `[AUTO]` TC-001, TC-002, TC-008 en verde.
- `[AUTO]` Suite completa en verde (todos los tests afectados por el grep de `GastoParticipante`/`.participantes` actualizados, no rotos).
- `[AUTO]` Migración `0014` corre limpia e idempotente contra Postgres real.

## T2 — `balance_service` sin reparto

### Gate Criteria
- `[AUTO]` TC-003, TC-004, TC-005 en verde.

## T3 — API/dashboard

### Gate Criteria
- `[AUTO]` `pytest tests/` completo sigue en verde.
- `[AUTO]` `GET .../balance` y `GET .../dashboard` devuelven el nuevo contrato.

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-006, TC-007 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra docker-compose: registrar un gasto (sin elegir
   participantes) → aparece en Gastos; Balance muestra el total gastado
   de la casa y el aporte de cada miembro, sin ninguna cifra de deuda ni
   transferencia sugerida.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001/TC-002 | ¿Quedó algún test o fixture que todavía crea `GastoParticipante` directamente? | Grep incompleto — un test file no detectado en la búsqueda inicial |
| TC-008 | ¿`_crear_gastos_en_cuotas` sigue dividiendo el importe total entre las N cuotas (sin relación a participantes)? | Eliminar por error también el reparto por cuotas al sacar el reparto por participante |
| TC-005 | ¿`BalanceCasa`/`calcular_balance` todavía exponen algún campo de deuda o transferencia? | No eliminar `Transferencia`/`sugerir_transferencias` por completo |
