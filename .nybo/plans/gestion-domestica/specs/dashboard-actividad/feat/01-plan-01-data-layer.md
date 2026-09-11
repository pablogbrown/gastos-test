# Task 1 — Data Layer: Historial de Actividad

## Scope
- `src/db/models/historial_actividad.py`
- `src/db/migrations/0004_historial_actividad.py`

## Changes
### Data Layer
- Tabla `historial_actividad`: id, casa_id (fk), tipo (enum: gasto_registrado|tarea_creada|tarea_completada|puntos_obtenidos|miembro_agregado), miembro_id (fk, nullable), fecha (datetime), descripcion (string). Append-only.

## Design Rationale
Una tabla genérica de eventos (en vez de una por tipo de acción) permite listar el historial completo con una sola query ordenada por fecha, cumpliendo REQ-002/REQ-003 sin joins múltiples.

## Dependencies
Ninguna dentro de esta spec (requiere `casas`/`miembros` de `casas-miembros`, cross-spec).

## Done When
- [ ] Migración corre limpia.
- [ ] Inserción y lectura ordenada por fecha verificadas (TC-005).

## Interfaces Produced
- `{name: "HistorialActividad", signature: "class HistorialActividad(id, casa_id, tipo, miembro_id, fecha, descripcion)", kind: "class"}`

## Standalone Verifiable
Sí.
