# T3 — API expone `moneda`

## Scope
- `src/api/routes/gastos.py`
- `src/api/routes/suscripciones.py`
- `tests/integration/api/gastos_moneda_routes.test.py` (nuevo)

## Changes
- `GastoCreate`: agregar `moneda: Optional[str] = None` (Optional a
  nivel de esquema, mismo criterio que `cuotas` — para que un valor
  inválido llegue al servicio y se rechace con 400 vía `ValidationError`
  en vez de un 422 genérico de Pydantic, TC-008).
- `GastoOut`: agregar `moneda: str`.
- `SuscripcionCreate`: agregar `moneda: Optional[str] = None`.
- `SuscripcionOut`: agregar `moneda: str`.
- `BalancePorMiembroOut`/`TransferenciaOut`: agregar `moneda: str`.
- `registrar_gasto_endpoint`/`crear_suscripcion_endpoint`: pasar
  `payload.moneda or "ARS"` al servicio correspondiente.
- `dashboard.py`: sin cambios — `DashboardResponse.balance` ya reutiliza
  `BalancePorMiembroOut` importado de `gastos.py`.

## Design Rationale
Mismo patrón aditivo que `cuotas`/`suscripcion_id` en `GastoOut`: un
campo `Optional` nuevo nunca rompe un cliente HTTP existente que no lo
envía ni lo lee.

## Dependencies
T2 (`registrar_gasto`/`crear_suscripcion` aceptan `moneda`).

## Done When
- [ ] TC-008 pasa (moneda inválida → 400).
- [ ] Un `GET .../balance` y un `GET .../suscripciones` devuelven `moneda` en cada fila.

## Interfaces Produced
- `GastoCreate.moneda`, `GastoOut.moneda`, `SuscripcionCreate.moneda`, `SuscripcionOut.moneda`.
- `BalancePorMiembroOut.moneda`, `TransferenciaOut.moneda`.

## Interfaces Consumed
- T2: `registrar_gasto`, `crear_suscripcion`, `calcular_balance`, `sugerir_transferencias`.

## Standalone Verifiable
Sí.
