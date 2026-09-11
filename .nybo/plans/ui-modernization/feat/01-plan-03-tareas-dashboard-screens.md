# Task 3 — Restyle: Tareas, Ranking, InicioCasa, HistorialActividad

## Scope
- `src/frontend/pages/Tareas.tsx`
- `src/frontend/pages/Ranking.tsx`
- `src/frontend/pages/InicioCasa.tsx`
- `src/frontend/pages/HistorialActividad.tsx`

## Changes
### Frontend — Screens
- `Tareas.tsx`: listado por estado (`Tabs` o `Chip` de filtro), formulario de creación (`TextField`, `Switch` para recurrente), botón "Marcar completada" (`Button`) — mismas llamadas a `tareasClient.ts`.
- `Ranking.tsx`: tabla ordenada (`Table`) con indicador visual de posición (`Chip`/ícono para el top 3) — misma llamada a `tareasClient.ts`.
- `InicioCasa.tsx`: layout de tarjetas (`Card`/`Grid`) para miembros, gastos recientes, balance, tareas pendientes/completadas y ranking — mismas llamadas a `dashboardClient.ts`.
- `HistorialActividad.tsx`: lista cronológica (`List`/`Timeline`-like con `List` + `ListItemIcon` por tipo de evento) — misma llamada a `dashboardClient.ts`.

## Design Rationale
Igual que T2: estas 4 pantallas comparten cliente de API (`tareasClient.ts`/`dashboardClient.ts`) y buena parte del patrón visual (tarjetas/listas), así que se restylean juntas.

## Dependencies
T1 (tema y shell deben existir). Independiente de T2 — ambas consumen T1 pero no se tocan entre sí (archivos disjuntos).

## Done When
- [ ] TC-003 pasa para estas 4 pantallas.
- [ ] Cada pantalla sigue funcionando end-to-end contra la API real.
- [ ] Build y lint limpios.

## Interfaces Produced
Ninguno.

## Standalone Verifiable
Sí, una vez T1 existe — independiente de T2.
