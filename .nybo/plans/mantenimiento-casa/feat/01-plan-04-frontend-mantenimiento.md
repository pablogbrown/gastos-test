# T4 — Pantalla "Mantenimiento"; banner en Inicio; nav agrupada con Tareas

## Scope
- `src/frontend/api/mantenimientoClient.ts` (nuevo).
- `src/frontend/pages/Mantenimiento.tsx` (nuevo).
- `src/frontend/api/dashboardClient.ts`.
- `src/frontend/pages/InicioCasa.tsx`.
- `src/frontend/AppNav.tsx`.
- `src/frontend/App.tsx`.
- `tests/unit/frontend/Mantenimiento.test.tsx` (nuevo).
- `tests/unit/frontend/InicioCasa.test.tsx`, `AppShell.test.tsx`.

## Changes
- `mantenimientoClient.ts`: `crearItem`, `listarItems`, `completarItem`,
  `agregarMaterial`, `actualizarMaterial` — mismo patrón que
  `tarjetasClient.ts`/`prestamosClient.ts`.
- `Mantenimiento.tsx`: formulario de alta (nombre, descripción, fecha
  estimada, toggle Recurrente + selector Periodicidad, lista de
  materiales a agregar con nombre/cantidad antes de crear el ítem) +
  listado con: chip de estado (clickeable solo para completar, mismo
  patrón que `Gastos.tsx`, pero sin volver atrás — completar es
  unidireccional a diferencia de pagado/a_pagar), y por ítem una lista
  desplegable de materiales con checkbox "conseguido" por cada uno
  (TC-009).
- `dashboardClient.ts`: `DashboardResponse` agrega
  `mantenimientoConAlerta: ItemMantenimientoAlerta[]`.
- `InicioCasa.tsx`: nueva sección de alerta (mismo patrón que
  `tarjetasConAlerta`) — un `Alert` por ítem próximo a vencer, `severity`
  `"error"` si ya venció, `"warning"` si no (TC-010).
- `AppNav.tsx`: agregar `{ value: "mantenimiento", label:
  "Mantenimiento", icon: <...Icon /> }` a `SECCIONES`/`Pantalla`;
  reemplazar la entrada suelta `"tareas"` de `GRUPOS_DESKTOP` por un
  grupo `{ label: "Tareas", pantallas: ["tareas", "mantenimiento"] }` —
  la barra inferior mobile sigue usando `SECCIONES` sin cambios.
- `App.tsx`: renderizar `<Mantenimiento casaId={...} />` para la sección
  `"mantenimiento"`.

## Design Rationale
"Tareas" pasa de suelta a grupo por el mismo mecanismo ya construido en
`nav-agrupada` — no hace falta ningún cambio estructural nuevo en
`AppNav.tsx`, solo declarar la nueva agrupación.

## Dependencies
T3 (`mantenimientoClient`, `mantenimientoConAlerta` en el dashboard).

## Done When
- [ ] TC-009 y TC-010 pasan.
- [ ] El TC-001 de `AppShell.test.tsx` (grupo activo se resalta con cualquiera de sus pantallas) sigue en verde con "Tareas" ahora como grupo.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T3: `ItemMantenimientoOut`, `MaterialOut`, `mantenimientoConAlerta`.

## Standalone Verifiable
Sí.
