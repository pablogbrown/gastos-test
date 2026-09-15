# Progress — Importar resumen de tarjeta en PDF

## Checklist

### Tasks
- [x] T1 — `pdf_resumen_parser` (puro); `Gasto.tarjeta_id`; dependencia `pdfplumber`
- [x] T2 — `resumen_importer_service`; helpers de cuotas/suscripción detectada
- [x] T3 — Endpoint de subida de PDF
- [x] T4 — Botón "Importar resumen" en Tarjetas

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Importar actualiza cierre/vencimiento/saldo de la tarjeta
- [x] `[TC-002]` *[INTEGRATION]* — Consumo en pesos crea gasto en ARS
- [x] `[TC-003]` *[INTEGRATION]* — Consumo en dólares crea gasto en USD
- [x] `[TC-004]` *[INTEGRATION]* — "C.04/06" crea solo las cuotas restantes
- [x] `[TC-005]` *[INTEGRATION]* — Comercio reconocido crea Suscripcion nueva (Administrador)
- [x] `[TC-006]` *[INTEGRATION]* — Comercio reconocido reutiliza Suscripcion existente
- [x] `[TC-007]` *[INTEGRATION]* — Comercio reconocido sin permiso cae a gasto suelto
- [x] `[TC-008]` *[INTEGRATION]* — Líneas de impuestos/cargos nunca generan gastos
- [x] `[TC-009]` *[INTEGRATION]* — PDF no reconocible rechazado, cero gastos creados (cubierto a nivel de parser en T1; integración completa en T2)
- [x] `[TC-010]` *[UNIT]* — Botón "Importar resumen" sube y muestra el resumen sin confirmación

## Completion Summary
4 tareas implementadas (T1-T4), 10/10 test cases resueltos a test
automatizado real, verify en verde a nivel de spec (243 pytest + 93
vitest, build/lint limpios, migración 0012 idempotente contra Postgres
real, smoke en vivo end-to-end contra docker-compose confirmando
REQ-001 a REQ-008/Outcome). 4 convenciones extraídas a memoria de
proyecto. Decisión `D001` (nueva dependencia `python-multipart`)
confirmada por el usuario y resuelta antes de `/nybo-ship`.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec creada — 4 tareas, 10 test cases. Depende de `gastos-multi-moneda` y `tarjetas-credito` (build en ese orden). Nueva dependencia de backend: `pdfplumber` (confirmada con el usuario). |
| 2 | 2026-09-15 | build | ready | pass | Pre-build: main (gastos-multi-moneda + tarjetas-credito shipped) mergeado sin conflictos, suite reverificada en verde, pusheado. T1-T4 implementados. Verify: 243 pytest + 93 vitest, build/lint limpios, migración 0012 idempotente contra Postgres real (efímera y persistida), smoke en vivo confirmado (screenshots en evidence/1/screenshots/). Curate: 4 convenciones extraídas (DBG-04, SERVP-03, SERVP-04, APIP-01). 1 decisión abierta no bloqueante (D001, python-multipart). |
