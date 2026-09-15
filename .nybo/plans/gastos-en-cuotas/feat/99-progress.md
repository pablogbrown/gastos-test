# Progress — Registrar un gasto en cuotas

## Checklist

### Tasks
- [x] T1 — `Gasto` guarda grupo/número/total de cuota
- [x] T2 — `registrar_gasto` genera N gastos en cuotas
- [x] T3 — `GastoCreate`/`GastoOut` exponen `cuotas`
- [x] T4 — `Gastos.tsx` ofrece cargar en cuotas

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — 3 cuotas con fechas consecutivas mes a mes
- [x] `[TC-002]` *[UNIT]* — Redondeo ajustado en la última cuota
- [x] `[TC-003]` *[INTEGRATION]* — Cuotas comparten grupo y número/total correctos
- [x] `[TC-004]` *[INTEGRATION]* — Sin cuotas, comportamiento idéntico a hoy
- [x] `[TC-005]` *[INTEGRATION]* — `cuotas=0` es rechazado
- [x] `[TC-006]` *[INTEGRATION]* — Cuota futura no infla el balance de hoy
- [x] `[TC-007]` *[UNIT]* — El formulario envía `cuotas` en el body

## Completion Summary
Las 4 tareas implementadas: columnas de cuota + migración 0008 (T1),
`registrar_gasto` genera N gastos mensuales consecutivos con
`_sumar_meses`/`_dividir_importe` reutilizado (T2), API expone `cuotas`/
`cuota_grupo_id`/`cuota_numero`/`cuota_total` (T3), formulario "Nuevo
gasto" ofrece un campo Cuotas opcional siguiendo el patrón vacío→undefined
de `fix-validacion-puntos-tarea` (T4). Las 7 TC pasan, más 3 tests de
regresión agregados (cuotas=1 se comporta como ausente, cuotas negativo
rechazado, HTTP 400/200 de cuotas). Suite completa: pytest y vitest en
verde, `npm run build`/`npm run lint` sin errores, migración 0008
verificada idempotente contra Postgres real.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec created — 4 tasks, 7 test cases. Depende de `balance-mensual` (build en ese orden). |
| 2 | 2026-09-15 | run | — | — | T1-T4 implementadas. 165 pytest (154 previos + 11 nuevos) + 74 vitest (72 previos + 2 nuevos) en verde; `npm run build`/`lint` limpios; migración 0008 corrida 2x contra Postgres real (idempotente). |
| 3 | 2026-09-15 | verify | verified | confirmed | Verify --auto: 165 pytest + 74 vitest, build/lint limpios, 7 TC resueltas. Smoke en vivo contra docker: 3 cuotas creadas desde la UI con fechas/descripciones correctas; balance de septiembre solo refleja la 1ra cuota ($40.000), balance de noviembre refleja la 3ra, balance de diciembre = 0. |
| 4 | 2026-09-15 | curate | — | — | `[SERVP-02]` agregado a services.md (aritmética de meses con stdlib, 2da confirmación independiente). Sin cambios en frontend.md (patrón vacío→undefined ya documentado). 3 suggestions registradas (coverage tool ausente, bug recurrente de `nybo results write`, cuota_grupo_id sin UI todavía). |
