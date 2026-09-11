# Task 4 — UI: Tareas, Ranking e Historial

## Scope
- `src/frontend/pages/Tareas.tsx`
- `src/frontend/pages/Ranking.tsx`
- `src/frontend/api/tareasClient.ts`

## Changes
### UI
- Pantalla "Tareas": listado por estado, formulario de creación (incluye toggle "recurrente" + frecuencia), botón "Marcar completada" visible solo si el usuario puede completarla (sin responsable, o es el responsable, o es admin).
- Pantalla "Ranking": tabla ordenada por puntos.
- Pantalla "Historial de tareas": tabla fecha/miembro/tarea/puntos.

## Design Rationale
Mismo patrón de UI delgada sobre la API real, consistente con `casas-miembros` y `gastos`.

## Dependencies
T3.

## Done When
- [ ] Flujo crear tarea → completar → ver en ranking e historial funciona end-to-end.
- [ ] Build succeeds.

## Interfaces Produced
Ninguno (task final).

## Standalone Verifiable
Sí, una vez T3 desplegado.
