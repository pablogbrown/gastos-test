# T1 — `MiembroOut` expone `usuario_id`

## Scope
- `src/api/schemas.py` — `MiembroOut`: nuevo campo `usuario_id`.
- `tests/integration/api/casas_routes.test.py` (o el archivo existente que ya cubre `GET .../miembros`) — TC-001.

## Changes
**API Route / Schema**
- `MiembroOut`: agregar `usuario_id: Optional[UUID] = None` (después de
  `id`, antes de `casa_id`, siguiendo el orden ya usado en el modelo
  `Miembro`). `orm_mode = True` ya hace que se serialice directo desde
  el atributo del modelo — sin tocar ningún servicio ni ruta.

## Design Rationale
Cambio aditivo puro: ningún consumidor existente del contrato
`MiembroOut` (frontend actual, tests existentes) se rompe por un campo
nuevo. `usuario_id` ya es un dato que cualquier miembro de la casa podría
inferir indirectamente (vía el flujo de agregar-por-email); exponerlo no
cambia el modelo de amenazas.

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] TC-001 pasa.
- [ ] `pytest tests/` completo sigue en verde.

## Interfaces Produced
- `MiembroOut.usuario_id` — `{name: "usuario_id", signature: "Optional[UUID]", kind: "export"}`

## Standalone Verifiable
Sí — TC-001 verifica la forma de la respuesta HTTP directamente.
