# Progress — Vista mensual del listado de Gastos

## Checklist

### Tasks
- [ ] T1 — `listar_gastos` acepta `mes` opcional
- [ ] T2 — `GET .../gastos?mes=`
- [ ] T3 — Selector de mes en Gastos.tsx

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Filtrado por mes
- [ ] `[TC-002]` *[INTEGRATION]* — Sin mes, todos los gastos (control)
- [ ] `[TC-003]` *[INTEGRATION]* — Filtrado vía HTTP
- [ ] `[TC-004]` *[UNIT]* — Selector pide el mes correcto
- [ ] `[TC-005]` *[UNIT]* — Mes actual preseleccionado
- [ ] `[TC-006]` *[UNIT]* — Dashboard de Inicio sin cambios (control)

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 3 tareas, 6 test cases. Independiente de `gastos-estado-pago` y `nav-agrupada` (se pueden buildear en cualquier orden entre sí). |
