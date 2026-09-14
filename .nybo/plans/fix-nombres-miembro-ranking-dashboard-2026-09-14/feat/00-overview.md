# Solution Overview — Ranking y dashboard muestran UUIDs crudos

## File Index
- [../spec.md](../spec.md)
- [10-verify.md](10-verify.md)
- [99-progress.md](99-progress.md)

### Task Index

| Task | File | Description | Dependencies |
|---|---|---|---|
| T1 | [01-plan-01-resolver-nombres.md](01-plan-01-resolver-nombres.md) | `Ranking`/`InicioCasa` reciben `miembros` y resuelven nombres | — |

## Problema y solución
`App.tsx` ya mantiene `miembros: Miembro[]` en estado (cargado vía
`listarMiembros`, usado hoy solo por `<Gastos>`). `Ranking.tsx` e
`InicioCasa.tsx` no reciben esa lista, así que no tienen forma de
traducir un id a un nombre — muestran el dato crudo que ya viene del
backend (`RankingEntryOut.miembroId`, `HistorialTareaOut.miembro_id`),
que nunca tuvo la intención de mostrarse directamente. La solución es
puramente de presentación en el cliente: pasar la prop ya disponible y
resolver, mismo patrón que `Gastos.tsx` (`nombreCategoria`) y
`Tareas.tsx` (resolución de `responsableId`) ya usan.

## Arquitectura
Sin cambios — ningún endpoint ni contrato de datos cambia; es
exclusivamente props + una función de resolución en 2 componentes de
presentación existentes.
