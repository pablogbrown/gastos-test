# T3 — Rutas de autos; mantenimiento acepta `auto_id`

## Scope
- `src/api/routes/autos.py` (nuevo).
- `src/api/main.py` — registrar el router.
- `src/api/routes/mantenimiento.py`.
- `tests/integration/api/autos_routes.test.py` (nuevo).

## Changes
- `autos.py`: `AutoCreate {marca, modelo, patente?, anio?}`, `AutoOut` —
  `POST/GET /casas/{id}/autos`.
- `mantenimiento.py`: `ItemMantenimientoCreate` agrega `auto_id:
  Optional[UUID] = None`; `listar_items_endpoint` agrega el query param
  opcional `autoId` (alias); `ItemMantenimientoOut`/
  `ItemMantenimientoAlertaOut` agregan `auto_id: Optional[UUID]`,
  `auto_nombre: Optional[str]` (aditivo).

## Design Rationale
Router propio para autos — mismo criterio que separó cada recurso HTTP
en su propio módulo a lo largo del proyecto.

## Dependencies
T2 (`auto_service`, `mantenimiento_service` con `auto_id`).

## Done When
- [ ] TC-001 a TC-005 pasan a nivel HTTP.

## Interfaces Produced
- `AutoOut`.

## Interfaces Consumed
- T2: `crear_auto`, `listar_autos`, `crear_item`, `listar_items`.

## Standalone Verifiable
Sí.
