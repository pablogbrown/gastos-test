# T1 — `Ranking`/`InicioCasa` resuelven nombre de miembro

## Scope
- `src/frontend/App.tsx` — pasar `miembros={miembros}` a `<Ranking>` y `<InicioCasa>`.
- `src/frontend/pages/Ranking.tsx` — nueva prop `miembros: Miembro[]`, resolver nombre por fila.
- `src/frontend/pages/InicioCasa.tsx` — nueva prop `miembros: Miembro[]`, resolver nombre en "Tareas completadas recientes".
- `tests/unit/frontend/Ranking.test.tsx` (o el archivo existente si ya cubre Ranking) — TC-001, TC-002.
- `tests/unit/frontend/InicioCasa.test.tsx` — TC-003.

## Changes
**UI**
- `RankingProps`/`InicioCasaProps`: agregar `miembros: Miembro[]`
  (import de `../api/casasClient`, mismo tipo que ya usa `GastosProps`).
- `Ranking.tsx`: agregar `function nombreDe(miembroId: string):
  string { return miembros.find((m) => m.id === miembroId)?.nombre ??
  miembroId; }` y usarla en la celda de la tabla en vez de
  `entrada.miembroId` directo.
- `InicioCasa.tsx`: misma función (o inline), aplicada al armar el
  `primary` de cada `ListItemText` en "Tareas completadas recientes"
  (`registro.miembro_id`).
- `App.tsx`: agregar `miembros={miembros}` a las dos invocaciones
  (`<Ranking casaId={casaActual.id} miembros={miembros} />`,
  `<InicioCasa casaId={casaActual.id} miembros={miembros} />`).

## Design Rationale
DRY con lo que ya existe: `Gastos.tsx`'s `nombreCategoria` y
`Balance.tsx`'s `nombreDe` son exactamente esta misma función aplicada a
otro tipo de id — se replica el patrón, no se inventa uno nuevo. Fallback
al id crudo (nunca una fila vacía) es el mismo criterio que
`Balance.tsx` ya usa.

## Dependencies
Ninguna.

## Done When
- [ ] TC-001, TC-002, TC-003 pasan.
- [ ] `npm run build` sin errores de tipos.
- [ ] `npm run test -- --run` completo sigue en verde.

## Interfaces Produced
Ninguna nueva — ambas props se agregan a interfaces ya exportadas
(`RankingProps`, `InicioCasaProps`).

## Standalone Verifiable
Sí — TC-001/002/003 renderizan cada componente con una prop `miembros`
mockeada, sin depender de `App.tsx` ni del backend real.
