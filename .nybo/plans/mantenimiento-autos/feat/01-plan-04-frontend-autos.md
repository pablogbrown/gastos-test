# T4 — Pantalla "Mantenimiento Autos"; nav

## Scope
- `src/frontend/api/autosClient.ts` (nuevo).
- `src/frontend/api/mantenimientoClient.ts`.
- `src/frontend/pages/MantenimientoAutos.tsx` (nuevo).
- `src/frontend/pages/InicioCasa.tsx`.
- `src/frontend/AppNav.tsx`.
- `src/frontend/App.tsx`.
- `tests/unit/frontend/MantenimientoAutos.test.tsx` (nuevo).
- `tests/unit/frontend/Mantenimiento.test.tsx` (control de regresión).

## Changes
- `autosClient.ts`: `crearAuto`, `listarAutos` — mismo patrón delgado
  que `tarjetasClient.ts`.
- `mantenimientoClient.ts`: `listarItems(casaId, autoId?)`,
  `crearItem(casaId, {..., autoId?})`; `ItemMantenimiento` agrega
  `autoId`/`autoNombre`.
- `MantenimientoAutos.tsx`: selector/alta de auto (marca, modelo,
  patente, año) + por cada auto registrado, su propio listado de ítems
  de mantenimiento (mismo formulario/checklist de materiales que
  `Mantenimiento.tsx`, parametrizado por `autoId`) — agrupados
  visualmente por auto (TC-006).
- `InicioCasa.tsx`: el texto de cada alerta usa `autoNombre` cuando está
  presente (ej. "Cambio de aceite (Toyota Corolla) vence en 3 días"),
  sin cambiar la estructura del banner ya construido.
- `AppNav.tsx`: agregar `"mantenimientoAutos"` a `SECCIONES`/`Pantalla`
  y al grupo desktop "Tareas" (junto a Tareas/Mantenimiento).
- `App.tsx`: renderizar `<MantenimientoAutos casaId={...} />`.

## Design Rationale
Mismo formulario/checklist de materiales que `Mantenimiento.tsx`
(duplicado, no extraído a un componente compartido en esta spec —
extraerlo es una mejora futura opcional, no bloqueante para el alcance
pedido).

## Dependencies
T3 (`autosClient`, `mantenimientoClient` con `autoId`).

## Done When
- [ ] TC-006 y TC-007 pasan.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T3: `AutoOut`, `ItemMantenimientoOut` (con `auto_id`/`auto_nombre`).

## Standalone Verifiable
Sí.
