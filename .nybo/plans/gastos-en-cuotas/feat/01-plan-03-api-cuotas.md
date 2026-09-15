# T3 — `GastoCreate`/`GastoOut` exponen `cuotas`

## Scope
- `src/api/routes/gastos.py` — `GastoCreate`, `GastoOut`, `registrar_gasto_endpoint`.

## Changes
**API Route / Schema**
- `GastoCreate`: agregar `cuotas: Optional[int] = None`.
- `GastoOut`: agregar `cuota_grupo_id: Optional[UUID] = None`,
  `cuota_numero: Optional[int] = None`, `cuota_total: Optional[int] = None`
  (`orm_mode` los toma directo del modelo, sin lógica extra).
- `registrar_gasto_endpoint`: pasar `payload.cuotas` a `registrar_gasto`.

## Design Rationale
Cambio aditivo puro sobre un endpoint ya existente — ningún consumidor
actual de `GastoCreate`/`GastoOut` se rompe por campos nuevos opcionales.

## Dependencies
T2 — necesita que `registrar_gasto` acepte `cuotas`.

## Done When
- [ ] `pytest tests/` completo sigue en verde.
- [ ] `POST /casas/{id}/gastos` con `cuotas` en el body crea las N
      filas esperadas (verificado ya en T2 a nivel servicio; acá se
      confirma que el payload HTTP llega correctamente).

## Interfaces Produced
Ninguna nueva — extiende schemas ya exportados.

## Standalone Verifiable
Sí.
