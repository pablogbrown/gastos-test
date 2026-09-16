# T3 — Selector de mes en Gastos.tsx

## Scope
- `src/frontend/api/gastosClient.ts`
- `src/frontend/pages/Gastos.tsx`
- `tests/unit/frontend/Gastos.test.tsx`

## Changes
- `gastosClient.ts`: `listarGastos(casaId: string, mes?: string):
  Promise<Gasto[]>` — agrega `?mes=` a la URL si está presente.
- `Gastos.tsx`: agrega un `TextField type="month"` (mismo patrón que
  `Balance.tsx`), estado `mes` inicializado al mes calendario actual
  (`new Date().toISOString().slice(0, 7)`, TC-005); `cargar()` pasa
  `mes` a `listarGastos`; cambiar el selector vuelve a pedir el listado
  (TC-004).

## Design Rationale
Mismo componente y mismo criterio de "mes actual preseleccionado" que
`Balance.tsx` — consistencia visual entre ambas pantallas.

## Dependencies
T2 (`GET .../gastos?mes=`).

## Done When
- [ ] TC-004 y TC-005 pasan.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T2: `GET /casas/{id}/gastos?mes=`.

## Standalone Verifiable
Sí.
