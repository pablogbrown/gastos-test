# Progress — Registrar un gasto en cuotas

## Checklist

### Tasks
- [ ] T1 — `Gasto` guarda grupo/número/total de cuota
- [ ] T2 — `registrar_gasto` genera N gastos en cuotas
- [ ] T3 — `GastoCreate`/`GastoOut` exponen `cuotas`
- [ ] T4 — `Gastos.tsx` ofrece cargar en cuotas

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — 3 cuotas con fechas consecutivas mes a mes
- [ ] `[TC-002]` *[UNIT]* — Redondeo ajustado en la última cuota
- [ ] `[TC-003]` *[INTEGRATION]* — Cuotas comparten grupo y número/total correctos
- [ ] `[TC-004]` *[INTEGRATION]* — Sin cuotas, comportamiento idéntico a hoy
- [ ] `[TC-005]` *[INTEGRATION]* — `cuotas=0` es rechazado
- [ ] `[TC-006]` *[INTEGRATION]* — Cuota futura no infla el balance de hoy
- [ ] `[TC-007]` *[UNIT]* — El formulario envía `cuotas` en el body

## Completion Summary
Not yet started.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec created — 4 tasks, 7 test cases. Depende de `balance-mensual` (build en ese orden). |
