# T4 — Pantalla "Préstamos"; entrada de navegación

## Scope
- `src/frontend/api/prestamosClient.ts` (nuevo).
- `src/frontend/pages/Prestamos.tsx` (nuevo).
- `src/frontend/AppNav.tsx`.
- `src/frontend/App.tsx`.
- `tests/unit/frontend/Prestamos.test.tsx` (nuevo).
- `tests/unit/frontend/AppShell.test.tsx` (ajustar conteos si corresponde).

## Changes
- `prestamosClient.ts`: `crearPrestamo`, `listarPrestamos`,
  `actualizarEstadoPrestamo` — mismo patrón que `tarjetasClient.ts`.
- `Prestamos.tsx`: formulario de alta (prestamista, deudor —
  `Select` de miembros de la casa; importe, moneda, fecha, descripción
  opcional) + listado con chip de estado clickeable (mismo patrón que el
  chip de estado de `Gastos.tsx`) — mismo componente visual, verde
  "Pagado" / naranja "Pendiente".
- `AppNav.tsx`: agregar `{ value: "prestamos", label: "Préstamos", icon:
  <...Icon /> }` a `SECCIONES` y al tipo `Pantalla`; agregar `"prestamos"`
  al grupo `"Gastos"` de `GRUPOS_DESKTOP` (junto a Gastos/Balance/
  Tarjetas/Suscripciones).
- `App.tsx`: renderizar `<Prestamos casaId={...} miembros={...} />` para
  la sección `"prestamos"`.

## Design Rationale
Chip de estado clickeable reutiliza el mismo patrón visual que
`Gastos.tsx` (`gastos-estado-pago`) — consistencia entre ambas pantallas
de estado pagado/pendiente.

## Dependencies
T3 (`prestamosClient`, endpoints de préstamos).

## Done When
- [ ] TC-007 y TC-008 pasan.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T3: `PrestamoOut`.

## Standalone Verifiable
Sí.
