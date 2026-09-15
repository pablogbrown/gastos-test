# T3 — `Balance.tsx` agrega el selector de mes

## Scope
- `src/frontend/pages/Balance.tsx`.
- `tests/unit/frontend/Balance.test.tsx` (nuevo, si no existe uno ya cubriendo esta pantalla) — TC-004, TC-005.

## Changes
**UI**
- Nuevo estado `mes: string` inicializado a `new Date().toISOString().slice(0, 7)`
  (formato `YYYY-MM`, mismo formato que espera el backend).
- `TextField type="month"` (nativo del navegador, mismo patrón que
  `type="date"` ya usado en `Tareas.tsx`/`Gastos.tsx`) enlazado a `mes`.
- `cargar()` pasa `mes` a `obtenerBalance(casaId, mes)`; el `useEffect`
  que dispara `cargar()` agrega `mes` a sus dependencias para
  refrescar al cambiar la selección.

## Design Rationale
Reutiliza el patrón nativo `type="month"` en vez de un `Select` con
opciones armadas a mano — el navegador ya resuelve la UI de elegir
año+mes, consistente con cómo esta app ya usa `type="date"` para fechas.

## Dependencies
T2 — necesita que el cliente HTTP acepte `mes`.

## Done When
- [ ] TC-004, TC-005 pasan.
- [ ] `npm run build` sin errores de tipos.
- [ ] `npm run test -- --run` completo sigue en verde.

## Interfaces Produced
Ninguna nueva.

## Standalone Verifiable
Sí — TC-004/005 renderizan `Balance` con `obtenerBalance` mockeado y
verifican el valor inicial del selector y que cambiarlo dispara un
nuevo llamado con el mes elegido.
