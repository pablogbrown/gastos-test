# T3 — Tareas con estado visual claro

## Scope
- `src/frontend/pages/Tareas.tsx`

## Changes
- Encabezado vía `PageHeader` (acción "Nueva tarea").
- Cada tarea como tarjeta de línea: color/ícono de estado (pendiente=neutral, completada=success con check), asignación visible (avatar del responsable, reutilizando el patrón de `Miembros`), y puntos como `Chip`.
- Botón "Marcar completada" preservado, visible solo al responsable (lógica existente sin cambio).

## Implementation Steps
1. Baseline: confirmar `Tareas.test.tsx` en verde.
2. Reemplazar encabezado por `PageHeader`.
3. Reconstruir cada tarea como tarjeta de línea con color/ícono de estado y avatar de responsable.
4. Re-correr el suite sin modificar queries.

## Design Rationale
Reutiliza el mismo `Avatar` de perfil introducido en T1 (Miembros) para el responsable de la tarea — consistencia visual entre "quién es" (Miembros) y "quién hace qué" (Tareas).

## Dependencies
Ninguna dentro de esta spec (no depende de T1 en el grafo formal, pero reutiliza el mismo patrón visual de avatar por convención).

## Done When
- [ ] TC-005, TC-007 pasan.
- [ ] `Tareas.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí.
