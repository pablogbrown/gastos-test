# T4 — Pantalla "Tarjetas"; banner de alerta en Inicio

## Scope
- `src/frontend/api/tarjetasClient.ts` (nuevo).
- `src/frontend/pages/Tarjetas.tsx` (nuevo).
- `src/frontend/AppNav.tsx` — agregar sección "Tarjetas".
- `src/frontend/App.tsx` — registrar la nueva pantalla.
- `src/frontend/api/dashboardClient.ts` — agregar `tarjetas_con_alerta`.
- `src/frontend/pages/InicioCasa.tsx` — banner de alerta.
- `tests/unit/frontend/Tarjetas.test.tsx` (nuevo).
- `tests/unit/frontend/InicioCasa.test.tsx`

## Changes
- `tarjetasClient.ts`: `crearTarjeta`, `listarTarjetas`,
  `actualizarTarjeta`, `eliminarTarjeta` — mismo patrón que
  `suscripcionesClient.ts` (`fetchAutenticado`, `parseJsonOrThrow`).
- `Tarjetas.tsx`: formulario de alta (banco, nombre, últimos 4 dígitos,
  cierre, vencimiento) + listado con edición inline de
  cierre/vencimiento/saldo y botón eliminar — mismo patrón visual que
  `Suscripciones.tsx`.
- `AppNav.tsx`: agregar `{ value: "tarjetas", label: "Tarjetas", icon:
  <CreditCardIcon /> }` a `SECCIONES` y al tipo `Pantalla`.
- `App.tsx`: renderizar `<Tarjetas casaId={...} />` para la sección `"tarjetas"`.
- `dashboardClient.ts`: `DashboardResponse` agrega `tarjetas_con_alerta:
  TarjetaAlerta[]`.
- `InicioCasa.tsx`: si `tarjetas_con_alerta.length > 0`, renderizar un
  `Alert severity="warning"` (o `"error"` si `vencida`) por cada una,
  con el texto "`{nombre}` (`{banco}`) vence el `{fecha}` — quedan
  `{dias}` días" o "ya venció hace `{-dias}` días" si `vencida`.

## Design Rationale
Banner recalculado en cada carga de Inicio (sin `localStorage` ni
estado de "ya visto") — más simple, y la app no tiene notificaciones
persistentes hoy en ningún otro lado.

## Dependencies
T3 (`tarjetasClient`, `tarjetas_con_alerta` en el dashboard).

## Done When
- [ ] TC-008 y TC-009 pasan.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T3: `TarjetaOut`, `TarjetaAlertaOut`.

## Standalone Verifiable
Sí.
