# T4 — Selector en el formulario; chip clickeable en el listado

## Scope
- `src/frontend/api/gastosClient.ts`
- `src/frontend/pages/Gastos.tsx`
- `tests/unit/frontend/Gastos.test.tsx`

## Changes
- `gastosClient.ts`: `NuevoGasto`/`Gasto` agregan `estado?: 'pagado' |
  'a_pagar'` / `estado: string`; nueva función
  `actualizarEstadoGasto(casaId, gastoId, estado): Promise<Gasto>` (PATCH).
- `Gastos.tsx`: el formulario "Nuevo gasto" agrega un `Select` Estado
  (Pagado default / A pagar) junto a Moneda (TC-009). El listado agrega
  una columna Estado con un `Chip` clickeable — verde "Pagado" / naranja
  "A pagar" — que al hacer clic llama a `actualizarEstadoGasto` con el
  estado contrario al actual y refresca la fila (TC-010).

## Design Rationale
Un `Chip` clickeable en vez de un formulario de edición aparte — mismo
criterio liviano que ya usa `Suscripciones.tsx` para cancelar (un link,
no un modal).

## Dependencies
T3 (`estado` en la API, endpoint `PATCH`).

## Done When
- [ ] TC-009 y TC-010 pasan.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T3: `GastoOut.estado`, `PATCH /casas/{id}/gastos/{id}`.

## Standalone Verifiable
Sí.
