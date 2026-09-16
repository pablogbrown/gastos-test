# Progress — Vista mensual del listado de Gastos

## Checklist

### Tasks
- [x] T1 — `listar_gastos` acepta `mes` opcional
- [x] T2 — `GET .../gastos?mes=`
- [x] T3 — Selector de mes en Gastos.tsx

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Filtrado por mes
- [x] `[TC-002]` *[INTEGRATION]* — Sin mes, todos los gastos (control)
- [x] `[TC-003]` *[INTEGRATION]* — Filtrado vía HTTP
- [x] `[TC-004]` *[UNIT]* — Selector pide el mes correcto
- [x] `[TC-005]` *[UNIT]* — Mes actual preseleccionado
- [x] `[TC-006]` *[UNIT]* — Dashboard de Inicio sin cambios (control)

## Completion Summary
Build cycle 1: `ready`/`verified`. Antes de T1 se hizo `git merge origin/main`
(trae `gastos-estado-pago` y `nav-agrupada`, ya shippeadas) directamente en
la rama del spec — merge limpio (sin conflictos), suite completa corrida
como baseline (261 backend + 102 frontend) y push antes de empezar. Las 3
tareas implementadas sobre el estado post-merge de `gasto_service.py`,
`gastos.py` y `Gastos.tsx`. 268 backend + 105 frontend tests en verde,
build/lint limpios, smoke HTTP real contra Postgres (docker) confirmando
el filtro por mes end-to-end. Ver `evidence/1/build-results.md`.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 3 tareas, 6 test cases. Independiente de `gastos-estado-pago` y `nav-agrupada` (se pueden buildear en cualquier orden entre sí). |
| 2 | 2026-09-16 | build | verified | pass | Merge de `main` (gastos-estado-pago + nav-agrupada) pre-T1, sin conflictos. T1-T3 implementadas via TDD. 268 backend + 105 frontend tests, build/lint OK, smoke HTTP real contra Postgres OK. |
