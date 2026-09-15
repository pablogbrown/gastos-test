# Progress — Multi-moneda en gastos, cuotas y suscripciones

## Checklist

### Tasks
- [x] T1 — `Gasto`/`Suscripcion` guardan `moneda`; migración
- [x] T2 — Servicios propagan y separan por moneda
- [x] T3 — API expone `moneda`
- [x] T4 — Selector de moneda; Balance por secciones

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Gasto en USD persiste correctamente
- [x] `[TC-002]` *[INTEGRATION]* — Sin moneda, default ARS (control)
- [x] `[TC-003]` *[INTEGRATION]* — Balance separado por moneda con actividad en ambas
- [x] `[TC-004]` *[UNIT]* — Sin actividad en USD, ninguna fila USD
- [x] `[TC-005]` *[UNIT]* — Transferencias nunca cruzan moneda
- [x] `[TC-006]` *[INTEGRATION]* — Suscripción en USD genera gasto en USD
- [x] `[TC-007]` *[INTEGRATION]* — Cuotas mantienen la misma moneda
- [x] `[TC-008]` *[INTEGRATION]* — Moneda inválida rechazada con 400
- [x] `[TC-009]` *[UNIT]* — Formulario envía `moneda` en el body
- [x] `[TC-010]` *[UNIT]* — Balance renderiza secciones separadas sin total combinado

#### Outcome Smoke Test
Observado en vivo contra el docker-compose real (ciclo 1, ver
`evidence/1/build-results.md` § Verification): vía API directa se
registró un gasto en ARS y otro en USD el mismo día y `GET .../balance`
devolvió 2 filas separadas; vía UI real (browser) se registró un gasto
USD ($25, mostró `US$25` en el historial) y uno ARS ($500, mostró
`$500`), y la pantalla Balance con actividad en ambas monedas renderizó
dos secciones independientes "Pesos"/"Dólares", cada una con su propia
tabla y sus propias transferencias sugeridas, sin ningún total
combinado; cambiando a un mes sin actividad USD, la sección "Dólares"
desaparece por completo. `## Outcome` observado: **sí**.

## Completion Summary
Multi-moneda (ARS/USD) implementado en las 4 capas (modelo+migración,
servicios, API, frontend) — 10/10 test cases resueltos por tests
automatizados, ninguno `[E2E]`/`[MANUAL]` pendiente. Suite completa en
verde (203 pytest + 85 vitest), build/lint limpios, migración 0010
verificada idempotente contra Postgres real dos veces (efímero y
docker-compose local con tablas preexistentes). Outcome confirmado en
vivo tanto por API como por UI real. Listo para `/nybo-ship`.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec creada — 4 tareas, 10 test cases. Foundation para `tarjetas-credito` e `importar-resumen-tarjeta` (build en ese orden). |
| 2 | 2026-09-15 | build | verified | sí | Ciclo 1: 4 tareas implementadas TDD, verify en verde (203 pytest/1 skip + 85 vitest + build/lint + migración 0010 idempotente contra Postgres real x2), curate aplicado ([DBP-01] en db.md, gotcha de frontend.md reconfirmado 3ª vez). |
