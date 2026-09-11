# Task 3 — API Routes: Tareas y Ranking

## Scope
- `src/api/routes/tareas.py`

## Changes
### API Route
- `POST /casas/{casaId}/tareas` → `crear_tarea`.
- `PATCH /casas/{casaId}/tareas/{tareaId}` → cambia estado; si pasa a `completada` invoca `completar_tarea` y luego `procesar_recurrencia`.
- `GET /casas/{casaId}/tareas` → listado, filtrable por estado.
- `GET /casas/{casaId}/ranking` → `calcular_ranking`.
- `GET /casas/{casaId}/tareas/historial` → historial de finalizaciones.

## Design Rationale
Rutas delgadas sobre T2, mismo patrón que las otras specs de la feature.

## Dependencies
T2.

## Done When
- [ ] Contratos HTTP verificados (400 sin nombre/puntos, 409 al completar una tarea ya completada).
- [ ] Build succeeds.

## Interfaces Produced
- `{name: "tareas_router", signature: "APIRouter", kind: "export"}`

## Standalone Verifiable
Sí.
