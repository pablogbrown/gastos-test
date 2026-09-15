# T2 — Servicios propagan y separan por moneda

## Scope
- `src/services/gasto_service.py`
- `src/services/suscripcion_service.py`
- `src/services/balance_service.py`
- `tests/integration/services/gasto_moneda.test.py` (nuevo)
- `tests/integration/services/suscripcion_moneda.test.py` (nuevo)
- `tests/unit/services/balance_moneda.test.py` (nuevo)

## Changes
**`gasto_service.py`**
- `registrar_gasto(..., moneda: str = "ARS")`: valida `moneda in
  {"ARS", "USD"}`, si no `raise ValidationError`. Persiste en `Gasto.moneda`.
- `_crear_gastos_en_cuotas`: recibe y propaga `moneda` a cada una de las
  N cuotas generadas (TC-007) — misma moneda en todas las partes de una
  misma compra.

**`suscripcion_service.py`**
- `crear_suscripcion(..., moneda: str = "ARS")`: misma validación,
  persiste en `Suscripcion.moneda`.
- `generar_gastos_pendientes`: al generar el gasto mensual de una
  suscripción, copia `suscripcion.moneda` al `Gasto.moneda` generado
  (TC-006) — llama a `registrar_gasto(..., moneda=suscripcion.moneda)`.

**`balance_service.py`**
- `BalancePorMiembro`: agregar campo `moneda: str`.
- `calcular_balance`: agrupar `pagos`/`correspondientes` por
  `(miembro_id, moneda)` en vez de solo `miembro_id`. Para `"ARS"`,
  mantener el comportamiento actual (una fila por cada miembro de la
  casa, incluso en 0 — TC-004 control). Para `"USD"`, emitir una fila
  solo para los miembros con pago o correspondencia distinta de cero en
  dólares ese mes (TC-004) — nunca una fila USD en 0 para toda la casa.
- `Transferencia`: agregar campo `moneda: str`.
- `sugerir_transferencias`: recibe la lista plana multi-moneda de
  `calcular_balance`; agrupar internamente por `moneda` (`dict[str,
  list[BalancePorMiembro]]`) y correr el algoritmo greedy existente por
  separado dentro de cada grupo — nunca comparar/emparejar entre grupos
  de moneda distinta (TC-005). Cada `Transferencia` resultante lleva la
  `moneda` de su grupo.

## Design Rationale
Agrupar por `(miembro, moneda)` en vez de devolver una estructura
anidada por moneda mantiene `calcular_balance`/`sugerir_transferencias`
devolviendo listas planas — el mismo tipo de retorno que ya consume la
API (T3) y el dashboard, solo con un campo más por fila. Evita una
segunda forma de "balance" en el sistema.

## Dependencies
T1 (`Gasto.moneda`/`Suscripcion.moneda`).

## Done When
- [ ] TC-001 a TC-007 pasan.
- [ ] Suite completa en verde (incluye tests existentes de cuotas/suscripciones — deben seguir pasando sin cambios de comportamiento en ARS).

## Interfaces Produced
- `registrar_gasto(..., moneda: str = "ARS")`.
- `crear_suscripcion(..., moneda: str = "ARS")`.
- `BalancePorMiembro.moneda`, `Transferencia.moneda`.

## Standalone Verifiable
Sí (vía tests de integración de servicios, sin pasar por HTTP).
