# Task 1 — Data Layer: Tarea e Historial

## Scope
- `src/db/models/tarea.py`
- `src/db/models/historial_tarea.py`
- `src/db/migrations/0003_tareas.py`

## Changes
### Data Layer
- Tabla `tareas`: id, casa_id (fk), nombre, descripcion (nullable), puntos (int), responsable_id (fk miembro, nullable), fecha_prevista (nullable), estado (enum: pendiente|en_curso|completada, default pendiente), recurrente (boolean, default false), frecuencia (nullable, ej. "diaria"|"semanal"|"quincenal").
- Tabla `historial_tarea`: id, tarea_id (fk), miembro_id (fk), completada_en (datetime), puntos_obtenidos (int). Inmutable — nunca se actualiza ni borra tras insertarse.

## Design Rationale
`historial_tarea` como tabla append-only garantiza que los puntos otorgados quedan auditables incluso si la Tarea original cambia de nombre o puntaje después.

## Dependencies
Requiere `casas`/`miembros` de la spec `casas-miembros` (cross-spec).

## Done When
- [ ] TC-003 verificado (estado por defecto = pendiente).
- [ ] Migración corre limpia.

## Interfaces Produced
- `{name: "Tarea", signature: "class Tarea(id, casa_id, nombre, descripcion, puntos, responsable_id, fecha_prevista, estado, recurrente, frecuencia)", kind: "class"}`
- `{name: "HistorialTarea", signature: "class HistorialTarea(id, tarea_id, miembro_id, completada_en, puntos_obtenidos)", kind: "class"}`

## Standalone Verifiable
Sí, contra una base con casas/miembros ya sembrados.
