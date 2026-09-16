# T3 — API expone `estado`; endpoint de actualización

## Scope
- `src/api/routes/gastos.py`
- `tests/integration/api/gastos_estado_routes.test.py` (nuevo)

## Changes
- `GastoCreate`: agregar `estado: Optional[str] = None` (Optional a
  nivel de esquema, mismo criterio que `moneda`/`cuotas` — para que un
  valor inválido llegue al servicio y se rechace con 400 vía
  `ValidationError`, no un 422 genérico).
- `GastoOut`: agregar `estado: str`.
- `registrar_gasto_endpoint`: pasar `payload.estado or "pagado"` al
  servicio.
- Nuevo schema `GastoEstadoUpdate {estado: str}`.
- Nueva ruta `PATCH /casas/{casa_id}/gastos/{gasto_id}` →
  `actualizar_estado_gasto(casa_id, gasto_id, payload.estado, actor)`,
  responde `GastoOut` (200). `ValidationError` → 400, `NotFoundError` →
  404.

## Design Rationale
Mismo patrón aditivo que `moneda`/`cuotas` en `GastoOut`. El `PATCH` es
el primer endpoint de edición de un gasto ya creado — se acota
deliberadamente a un solo campo (`estado`) en vez de un update genérico,
porque es lo único que esta spec necesita exponer.

## Dependencies
T2 (`actualizar_estado_gasto`).

## Done When
- [ ] TC-007 pasa (estado inválido → 400 en creación y en update).
- [ ] Un `PATCH .../gastos/{id}` cambia el estado y lo refleja en la respuesta.

## Interfaces Produced
- `GastoCreate.estado`, `GastoOut.estado`, `GastoEstadoUpdate`.

## Interfaces Consumed
- T2: `registrar_gasto`, `actualizar_estado_gasto`.

## Standalone Verifiable
Sí.
