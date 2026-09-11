# Task 4 — UI: Pantalla Principal e Historial de Actividad

## Scope
- `src/frontend/pages/InicioCasa.tsx`
- `src/frontend/pages/HistorialActividad.tsx`
- `src/frontend/api/dashboardClient.ts`

## Changes
### UI
- Pantalla "Inicio de la casa": secciones Miembros, Gastos recientes, Balance, Tareas pendientes, Tareas completadas recientes, Ranking — cada una con estado vacío legible.
- Pantalla "Historial de actividad": lista cronológica descendente con ícono/color por tipo de evento.

## Design Rationale
Reutiliza los mismos componentes de tabla/lista ya construidos en `gastos` y `tareas-puntos` donde sea posible, evitando duplicar UI de listados.

## Dependencies
T3.

## Done When
- [ ] TC-001 verificado manualmente contra datos de ejemplo (equivalente al caso de uso del documento, §19).
- [ ] TC-002 verificado sobre una casa vacía.
- [ ] Build succeeds.

## Interfaces Produced
Ninguno (task final de la feature completa).

## Standalone Verifiable
Sí, una vez T3 desplegado y con `gastos`/`tareas-puntos` implementados.
