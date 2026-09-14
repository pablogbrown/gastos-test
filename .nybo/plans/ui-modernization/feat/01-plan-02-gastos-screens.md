# Task 2 — Restyle: Miembros, Gastos, Balance

## Scope
- `src/frontend/pages/Miembros.tsx`
- `src/frontend/pages/Gastos.tsx`
- `src/frontend/pages/Balance.tsx`

## Changes
### Frontend — Screens
- `Miembros.tsx`: tabla de miembros (`Table`/`List` de MUI) con estado activo/inactivo (`Chip`), formulario de alta (`TextField`), acción "Desactivar" (`Button`/`IconButton`) visible solo para Administrador — mismo comportamiento y llamadas a `casasClient.ts` ya existentes.
- `Gastos.tsx`: formulario de registro (`TextField`, `Select` para categoría, `Checkbox` para "todos los miembros") + tabla/lista de historial con `Table` de MUI — mismas llamadas a `gastosClient.ts`.
- `Balance.tsx`: tabla de balance (`Table`) + lista de transferencias sugeridas (`List`/`Card`) — mismas llamadas a `gastosClient.ts`.

## Design Rationale
Agrupar estas 3 pantallas en una task (en vez de una por pantalla) porque comparten el mismo cliente de API (`gastosClient.ts`/`casasClient.ts`) y el mismo patrón de componentes (tabla + formulario) — una sola pasada de restyle cubre las tres de forma coherente.

## Dependencies
T1 (tema y shell deben existir para que estas pantallas los consuman).

## Done When
- [ ] TC-003 pasa para estas 3 pantallas.
- [ ] Cada pantalla sigue funcionando end-to-end contra la API real (mismos flujos ya verificados manualmente en la sesión anterior).
- [ ] Build y lint limpios.

## Interfaces Produced
Ninguno (no se exportan símbolos nuevos consumidos por otras tasks).

## Standalone Verifiable
Sí, una vez T1 existe — estas 3 pantallas no dependen de T3.
