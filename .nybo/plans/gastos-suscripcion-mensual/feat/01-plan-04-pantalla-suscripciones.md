# T4 — Pantalla "Suscripciones" + creación desde Gastos

## Scope
- `src/frontend/api/suscripcionesClient.ts` (nuevo).
- `src/frontend/pages/Suscripciones.tsx` (nuevo).
- `src/frontend/pages/Gastos.tsx` — modo "Suscripción mensual".
- `src/frontend/AppNav.tsx` — nueva sección "Suscripciones".
- `src/frontend/App.tsx` — wiring de la pantalla nueva.
- `tests/unit/frontend/Suscripciones.test.tsx` (nuevo) — TC-006.
- `tests/unit/frontend/Gastos.test.tsx` — TC-007.

## Changes
**UI**
- `suscripcionesClient.ts`: `crearSuscripcion`, `listarSuscripciones`,
  `cancelarSuscripcion` — mismo patrón delgado que `gastosClient.ts`.
- `Suscripciones.tsx`: tabla con descripción/importe/categoría/estado;
  botón "Cancelar" visible solo si `activa` y `rolUsuarioActual ===
  "admin"` (prop nueva, mismo patrón que `Miembros.tsx`).
- `Gastos.tsx`: el formulario "Nuevo gasto" gana un selector "Tipo de
  gasto": Único (default) / En cuotas / Suscripción mensual — mutuamente
  excluyente con el campo Cuotas de `gastos-en-cuotas` (elegir
  "Suscripción mensual" oculta/ignora Cuotas). Si el tipo es
  "Suscripción mensual", el envío llama a `crearSuscripcion` en vez de
  `registrarGasto` (no hay reparto de participantes explícito en el
  formulario para este modo — siempre "todos los miembros", igual que
  `crear_suscripcion` ya hace del lado del servicio).
- `AppNav.tsx`: agregar `"suscripciones"` a `Pantalla` y una entrada en
  `SECCIONES` (ícono `SubscriptionsIcon` de `@mui/icons-material`, ya
  cubierto por la dependencia existente).
- `App.tsx`: agregar el `case` de render para `"suscripciones"`, pasando
  `rolUsuarioActual` (ya resuelto por `resolver-rol-usuario-en-casa`).

## Design Rationale
Un solo formulario en Gastos con un selector de tipo, en vez de un
formulario separado para suscripciones — desde la perspectiva de quien
carga un gasto, "único / en cuotas / suscripción" es una sola decisión,
no dos pantallas distintas.

## Dependencies
T3 — necesita las rutas HTTP nuevas.

## Done When
- [ ] TC-006, TC-007 pasan.
- [ ] `npm run build` sin errores de tipos.
- [ ] `npm run test -- --run` completo sigue en verde.

## Interfaces Produced
Ninguna nueva de negocio — nuevos módulos de cliente/pantalla, sin
efecto en contratos ya exportados.

## Standalone Verifiable
Sí — TC-006/007 renderizan cada pantalla/formulario con mocks, sin
depender del backend real.
