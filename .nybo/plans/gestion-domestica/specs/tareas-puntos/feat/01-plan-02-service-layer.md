# Task 2 — Service Layer: Tareas, Puntos y Ranking

## Scope
- `src/services/tarea_service.py`
- `src/services/ranking_service.py`

## Changes
### Service Logic
- `crear_tarea(casa_id, nombre, puntos, descripcion?, responsable_id?, fecha_prevista?, recurrente?, frecuencia?, actor)`: valida `requiere_membresia_activa`, valida nombre y puntos obligatorios (TC-002), crea en estado `pendiente` (TC-003).
- `completar_tarea(tarea_id, miembro_id, actor)`: valida que la tarea no esté ya completada (TC-006), valida que si tiene responsable asignado solo ese miembro (o un admin) pueda completarla, si no tiene responsable cualquier miembro activo puede hacerlo (TC-004); inserta `HistorialTarea` con los puntos de la tarea (TC-005) y marca `estado=completada`.
- `procesar_recurrencia(tarea_completada)`: si `recurrente=true`, crea una nueva instancia de Tarea en estado `pendiente` según `frecuencia` (TC-009).
- `calcular_ranking(casa_id)`: agrega `sum(puntos_obtenidos)` de `HistorialTarea` por `miembro_id`, incluye miembros desactivados con puntos históricos, ordena descendente (TC-007, TC-008).

## Design Rationale
Separar `ranking_service` de `tarea_service` respeta SRP: el ranking es una vista agregada de solo lectura que no debería acoplarse a la lógica de mutación de tareas.

## Dependencies
T1; guard de membresía/permisos de la spec `casas-miembros` (cross-spec).

## Done When
- [ ] TC-001 a TC-009 pasan.
- [ ] `completar_tarea` nunca inserta más de un `HistorialTarea` por finalización.
- [ ] Build y tipos compilan.

## Interfaces Produced
- `{name: "crear_tarea", signature: "(casa_id, nombre, puntos, descripcion, responsable_id, fecha_prevista, recurrente, frecuencia, actor) -> Tarea", kind: "function"}`
- `{name: "completar_tarea", signature: "(tarea_id: UUID, miembro_id: UUID, actor: UUID) -> HistorialTarea", kind: "function"}`
- `{name: "calcular_ranking", signature: "(casa_id: UUID) -> {miembroId, puntos}[]", kind: "function"}`

## Standalone Verifiable
Sí, con T1 disponible y el guard de membresía mockeado.
