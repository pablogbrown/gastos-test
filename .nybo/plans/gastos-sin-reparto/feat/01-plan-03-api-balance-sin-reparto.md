# T3 — API/`dashboard_service` reflejan el nuevo contrato

## Scope
- `src/api/routes/gastos.py`
- `src/services/dashboard_service.py`
- `src/api/routes/dashboard.py`
- `tests/integration/api/gastos_routes.test.py` y variantes (`_moneda`, `_estado`, `_mes`) que toquen `BalanceResponse`/`participantes`
- `tests/integration/api/dashboard_routes.test.py`
- `tests/unit/services/dashboard_service.test.py`

## Changes
- `gastos.py`: eliminar `ParticipanteOut`; `GastoCreate`/`GastoOut`
  eliminan `participantes`. `BalancePorMiembroOut`/`TransferenciaOut` se
  reemplazan por `TotalCasaOut {moneda, total_gastos}` y `AporteOut
  {miembro_id, nombre, total, moneda}`; `BalanceResponse` pasa a
  `{totales: List[TotalCasaOut], aportes: List[AporteOut]}` (sin
  `transferencias`). `obtener_balance_endpoint` deja de llamar a
  `sugerir_transferencias` (ya no existe).
- `dashboard_service.DashboardCasa.balance`: cambia de tipo a
  `BalanceCasa` (importado de `balance_service`).
- `dashboard.py`: `DashboardResponse.balance` usa el mismo nuevo
  contrato (`TotalCasaOut`/`AporteOut`, reexportados o redefinidos según
  convenga — mismo criterio que ya reutiliza `BalancePorMiembroOut` hoy).

## Design Rationale
Mismo patrón aditivo/reemplazo directo ya usado en cada spec anterior
que tocó `GastoOut`/`BalanceResponse` — el contrato de Balance cambia de
forma explícita (no es aditivo esta vez, porque el concepto en sí
cambió), documentado en `spec.md`/`00-overview.md`.

## Dependencies
T2 (`BalanceCasa`).

## Done When
- [ ] `POST .../gastos` ya no acepta `participantes` en el body (se ignora o rechaza, a elección del implementador, pero nunca genera reparto).
- [ ] `GET .../balance` devuelve la forma `{totales, aportes}`.
- [ ] `GET .../dashboard` refleja el mismo contrato en su campo `balance`.
- [ ] Suite completa en verde.

## Interfaces Produced
- `TotalCasaOut`, `AporteOut` (schemas).

## Interfaces Consumed
- T2: `BalanceCasa`, `calcular_balance`.

## Standalone Verifiable
Sí.
