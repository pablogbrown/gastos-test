# Task 2 — Service Layer: Registro de Actividad y Agregación del Dashboard

## Scope
- `src/services/actividad_service.py`
- `src/services/dashboard_service.py`

## Changes
### Service Logic
- `registrar_actividad(casa_id, tipo, miembro_id, descripcion)`: inserta una fila en `historial_actividad`. Se invoca desde `gasto_service.registrar_gasto` (tipo `gasto_registrado`) y desde `tarea_service.crear_tarea`/`completar_tarea` (tipos `tarea_creada`/`tarea_completada`/`puntos_obtenidos`) — hooks agregados en las specs `gastos` y `tareas-puntos` como llamada directa al finalizar cada operación (TC-003, TC-004).
- `obtener_actividad(casa_id)`: devuelve `historial_actividad` ordenado por fecha descendente (TC-005).
- `armar_dashboard(casa_id)`: agrega miembros activos, últimos 10 gastos, balance (`balance_service.calcular_balance`), tareas en estado pendiente, últimas 10 tareas completadas, ranking (`ranking_service.calcular_ranking`); cada sección vacía si no hay datos, sin lanzar error (TC-002).

## Design Rationale
`dashboard_service` es puramente de lectura/agregación — no muta estado ni duplica lógica de negocio ya resuelta en `balance_service`/`ranking_service`, evitando una segunda fuente de verdad para esos cálculos.

## Dependencies
T1; `balance_service` (spec `gastos`) y `tarea_service`/`ranking_service` (spec `tareas-puntos`), cross-spec.

## Done When
- [ ] TC-002, TC-003, TC-004, TC-005 pasan.
- [ ] `armar_dashboard` no lanza error sobre una casa sin datos.
- [ ] Build y tipos compilan.

## Interfaces Produced
- `{name: "registrar_actividad", signature: "(casa_id, tipo, miembro_id, descripcion) -> HistorialActividad", kind: "function"}`
- `{name: "obtener_actividad", signature: "(casa_id: UUID) -> HistorialActividad[]", kind: "function"}`
- `{name: "armar_dashboard", signature: "(casa_id: UUID) -> DashboardCasa", kind: "function"}`

## Standalone Verifiable
Sí, con T1 y los servicios de `gastos`/`tareas-puntos` disponibles (o mockeados).
