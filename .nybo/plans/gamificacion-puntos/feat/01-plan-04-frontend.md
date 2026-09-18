# T4 — Frontend: niveles, rachas, logros y meta de la casa

## Scope
- `src/frontend/pages/Ranking.tsx`:
  - Selector de mes (mismo componente/criterio que `Balance.tsx`/
    `Gastos.tsx`, mes actual preseleccionado), pasado a
    `obtenerRanking(casaId, mes)`.
  - Chip de nivel y "🔥 {racha} días" por fila de la tabla.
  - Nueva sub-sección "Logros" (mismo patrón visual que "Historial de
    tareas" en `Tareas.tsx`): lista de logros desbloqueados por
    miembro, vía `listarLogros(casaId)`.
- `src/frontend/pages/Miembros.tsx`: campo "Meta de puntos mensual"
  (número) + botón guardar, visible solo si
  `puedeGestionarMiembros(rolUsuarioActual)` (mismo guard ya usado
  para agregar/desactivar miembros).
- `src/frontend/pages/InicioCasa.tsx`: card "Meta de la casa" con
  `LinearProgress` (MUI) — puntos acumulados / meta, porcentaje —
  renderizada solo si `dashboard.metaCasa` no es `null`.

## Dependencies
T1, T2, T3 (consume sus APIs).

## Done When
- TC-007/TC-008 pasan.
- Suite frontend completa sin regresión.

## Verifiability
UNIT — extender `tests/unit/frontend/Ranking.test.tsx`,
`Miembros.test.tsx`, `InicioCasa.test.tsx` (los tres ya existen).
