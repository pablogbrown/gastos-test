# T3 — Endpoints de resúmenes (listar + pagar) + 409 en importar

## Scope
`src/api/routes/tarjetas.py`:
- Nuevo schema `ResumenTarjetaOut` (`id, tarjeta_id, fecha_cierre,
  fecha_vencimiento, saldo_ars, saldo_usd, gastos_creados, estado,
  importado_en`, `orm_mode = True`).
- `ResumenImportadoOut` gana el campo `resumen_id: UUID`.
- Nuevo `GET /casas/{casa_id}/tarjetas/{tarjeta_id}/resumenes` →
  `response_model=list[ResumenTarjetaOut]`, delega en
  `resumen_importer_service.listar_resumenes`; mapea `NotFoundError` →
  404.
- Nuevo `PATCH /casas/{casa_id}/tarjetas/{tarjeta_id}/resumenes/
  {resumen_id}/pagar` → `response_model=ResumenTarjetaOut`, delega en
  `pagar_resumen`; mapea `NotFoundError` → 404, `ConflictError` → 409.
- `importar_resumen_endpoint`: agregar el mapeo `except ConflictError as
  exc: raise HTTPException(status_code=status.HTTP_409_CONFLICT,
  detail=str(exc)) from exc` (mismo criterio que `tareas.py`/
  `mantenimiento.py`).

## Dependencies
T2 (necesita `pagar_resumen`/`listar_resumenes` y el `ConflictError` de
duplicado).

## Done When
- `tests/integration/api/tarjetas_routes.test.py` (extender el
  existente si ya cubre `/resumen`, si no crearlo) cubre: importar dos
  veces el mismo resumen → 409 en la segunda; `GET .../resumenes`
  devuelve la lista; `PATCH .../resumenes/{id}/pagar` marca todo como
  pagado y responde 409 si se llama de nuevo sobre el mismo resumen ya
  pagado.

## Verifiability
INTEGRATION — `tests/integration/api/tarjetas_routes.test.py`.
