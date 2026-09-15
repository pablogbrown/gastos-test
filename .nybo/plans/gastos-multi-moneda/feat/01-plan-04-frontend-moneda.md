# T4 — Selector de moneda; Balance por secciones

## Scope
- `src/frontend/api/gastosClient.ts`
- `src/frontend/api/suscripcionesClient.ts`
- `src/frontend/pages/Gastos.tsx`
- `src/frontend/pages/Suscripciones.tsx`
- `src/frontend/pages/Balance.tsx`
- `src/frontend/pages/InicioCasa.tsx`
- `tests/unit/frontend/Gastos.test.tsx`
- `tests/unit/frontend/Balance.test.tsx`

## Changes
- `gastosClient.ts`: `NuevoGasto`/`BalancePorMiembro`/`Transferencia`
  agregan `moneda?: 'ARS' | 'USD'` / `moneda: string` según corresponda.
- `suscripcionesClient.ts`: `NuevaSuscripcion`/`Suscripcion` ídem.
- `Gastos.tsx`: el formulario "Nuevo gasto" agrega un `Select` Moneda
  (ARS/USD, default ARS) junto a Importe; se envía como `moneda` en el
  body (ausente → `undefined`, nunca fuerza `"ARS"` explícito, mismo
  patrón vacío→undefined ya usado para campos opcionales). El listado de
  gastos muestra el importe con prefijo `US$` cuando `moneda === "USD"`,
  `$` en caso contrario.
- `Suscripciones.tsx`: mismo selector Moneda en el formulario de alta.
- `Balance.tsx`: agrupa `balance.balances`/`balance.transferencias` por
  `moneda` y renderiza una sección por cada moneda presente (siempre
  "Pesos"; "Dólares" solo si hay al menos una fila con `moneda ===
  "USD"`) — cada sección con su propia tabla y sus propias
  transferencias sugeridas, sin ningún total combinado entre ambas
  (TC-010).
- `InicioCasa.tsx`: el mini-balance filtra a solo filas `moneda ===
  "ARS"` — vista rápida del dashboard, no reemplaza a la pantalla
  Balance completa.

## Design Rationale
El agrupamiento por moneda se hace en el cliente (no en el backend)
porque `BalanceResponse` ya es la misma lista plana que consume
`InicioCasa.tsx` — introducir una segunda forma de respuesta solo para
`Balance.tsx` hubiera duplicado el contrato sin necesidad.

## Dependencies
T3 (`moneda` expuesto en gastos/suscripciones/balance).

## Done When
- [ ] TC-009 y TC-010 pasan.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T3: `GastoOut.moneda`, `SuscripcionOut.moneda`, `BalancePorMiembroOut.moneda`, `TransferenciaOut.moneda`.

## Standalone Verifiable
Sí.
