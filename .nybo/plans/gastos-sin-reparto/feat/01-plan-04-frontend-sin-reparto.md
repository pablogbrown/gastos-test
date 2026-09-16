# T4 — `Gastos.tsx` sin selector; `Balance.tsx`/`InicioCasa.tsx` rediseñados

## Scope
- `src/frontend/api/gastosClient.ts`
- `src/frontend/pages/Gastos.tsx`
- `src/frontend/pages/Balance.tsx`
- `src/frontend/pages/InicioCasa.tsx`
- `src/frontend/App.tsx`
- `tests/unit/frontend/Gastos.test.tsx`, `Balance.test.tsx`, `InicioCasa.test.tsx`

## Changes
- `gastosClient.ts`: eliminar `NuevoGasto.participantes`, el tipo
  equivalente a `ParticipanteOut`, y `Gasto.participantes`.
  `BalancePorMiembro`/`Transferencia` se reemplazan por `TotalCasa
  {moneda, total_gastos}`/`AporteMiembro {miembro_id, nombre, total,
  moneda}`; `BalanceResponse` pasa a `{totales: TotalCasa[], aportes:
  AporteMiembro[]}`.
- `Gastos.tsx`: eliminar el `Checkbox` "Todos los miembros", el
  `FormGroup` de selección de participantes, los estados
  `todosLosMiembros`/`seleccionados` y la función `toggleParticipante`;
  el body de `registrarGasto` deja de incluir `participantes`. La prop
  `miembros` deja de usarse — eliminarla de `GastosProps` y de su uso en
  `App.tsx` (`<Gastos casaId={...} />`, sin `miembros`).
- `Balance.tsx`: rediseño completo de la sección por moneda — en vez de
  la tabla "Miembro / Pagó / Le correspondía / Balance" + "Transferencias
  sugeridas", mostrar el total gastado de la casa (`totales`) como texto
  destacado, y debajo una lista/tabla simple "Miembro — Aportó $X"
  (`aportes`) — sin ninguna columna de deuda ni sección de
  transferencias.
- `InicioCasa.tsx`: la sección "Balance" del dashboard usa el mismo
  nuevo contrato — mostrar el total de la casa en ARS (mismo criterio
  de "solo ARS en el mini-resumen" ya usado) en vez de la lista de
  `balance` por miembro con su cifra de deuda.

## Design Rationale
Sin selector de participantes, el formulario "Nuevo gasto" queda más
corto — un gasto se carga con los mismos campos que ya tenía (fecha,
descripción, importe, moneda, categoría, estado, cuotas) menos la
elección de con quién se reparte.

## Dependencies
T3 (`totales`/`aportes` en la API).

## Done When
- [ ] TC-006 y TC-007 pasan.
- [ ] `npm run build`/`npm run lint` sin errores.

## Interfaces Produced
Ninguna (consumidor final).

## Interfaces Consumed
- T3: `TotalCasaOut`, `AporteOut`.

## Standalone Verifiable
Sí.
