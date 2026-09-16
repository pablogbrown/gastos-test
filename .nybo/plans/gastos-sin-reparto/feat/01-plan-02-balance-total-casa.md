# T2 — `balance_service`: total de la casa + aportes informativos

## Scope
- `src/services/balance_service.py`
- `tests/unit/services/balance_service.test.py`, `balance_moneda.test.py` (reescribir contra el nuevo contrato)

## Changes
- Eliminar `BalancePorMiembro`, `Transferencia`, `sugerir_transferencias`,
  `_sugerir_transferencias_de_una_moneda`.
- Nuevas dataclasses:
  ```python
  @dataclass
  class TotalCasaPorMoneda:
      moneda: str
      total_gastos: Decimal

  @dataclass
  class AportePorMiembro:
      miembro_id: UUID
      nombre: str
      total: Decimal
      moneda: str

  @dataclass
  class BalanceCasa:
      totales: List[TotalCasaPorMoneda]
      aportes: List[AportePorMiembro]
  ```
- `calcular_balance(casa_id, mes=None) -> BalanceCasa`:
  - `totales`: `SUM(Gasto.importe)` agrupado por `moneda`, filtrado por
    casa y mes (TC-003) — una fila por cada moneda con actividad ese mes
    (incluida ARS en $0 si no hubo gastos, mismo criterio que ya existe
    para "siempre mostrar ARS").
  - `aportes`: `SUM(Gasto.importe)` agrupado por `(pagado_por, moneda)`
    (TC-004) — mismo criterio ya establecido en `gastos-multi-moneda`:
    ARS siempre trae una fila por cada miembro de la casa (incluso en
    $0); cualquier otra moneda solo trae filas para miembros con
    actividad real ese mes.
  - Ya no depende de `GastoParticipante` en absoluto (T1 ya la eliminó).

## Design Rationale
Ver `00-overview.md` — por qué `sugerir_transferencias` no se reemplaza
por ningún equivalente acá (esa función queda cubierta conceptualmente
por `prestamos-entre-miembros`, un registro explícito, no un cálculo
derivado).

## Dependencies
T1 (`GastoParticipante` eliminado; `gasto_service` ya no la referencia).

## Done When
- [ ] TC-003, TC-004 y TC-005 pasan.
- [ ] Ningún test de este archivo referencia `BalancePorMiembro`/`Transferencia`/`sugerir_transferencias`.

## Interfaces Produced
- `TotalCasaPorMoneda`, `AportePorMiembro`, `BalanceCasa`.
- `calcular_balance(casa_id, mes=None) -> BalanceCasa` (firma existente, tipo de retorno nuevo).

## Standalone Verifiable
Sí.
