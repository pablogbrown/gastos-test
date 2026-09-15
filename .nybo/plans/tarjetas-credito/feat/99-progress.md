# Progress — Gestión de tarjetas de crédito y alerta de vencimiento

## Checklist

### Tasks
- [x] T1 — Modelo `TarjetaCredito` + migración
- [x] T2 — `tarjeta_service` (CRUD + cálculo de alerta)
- [x] T3 — Rutas de tarjetas; dashboard expone alertas
- [x] T4 — Pantalla "Tarjetas"; banner en Inicio

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Alta de tarjeta con datos válidos
- [x] `[TC-002]` *[INTEGRATION]* — Alta sin banco rechazada con 400
- [x] `[TC-003]` *[INTEGRATION]* — Edición de vencimiento persiste
- [x] `[TC-004]` *[INTEGRATION]* — Baja saca la tarjeta del listado activo
- [x] `[TC-005]` *[UNIT]* — Vence en 3 días → aparece en alerta
- [x] `[TC-006]` *[UNIT]* — Ya vencida → aparece marcada como vencida
- [x] `[TC-007]` *[UNIT]* — Vence en 20 días → no aparece en alerta
- [x] `[TC-008]` *[UNIT]* — Banner se renderiza en Inicio
- [x] `[TC-009]` *[UNIT]* — Alta desde el formulario de la pantalla Tarjetas

## Completion Summary
4 tareas implementadas (modelo+migración, servicio, API+dashboard,
frontend), 9/9 test cases en verde, suite completa (223 pytest + 91
vitest), build/lint sin errores, migración 0011 idempotente contra
Postgres real, y smoke manual en vivo confirmando el `## Outcome` de
spec.md (banner de alerta renderizado en Inicio tras registrar una
tarjeta próxima a vencer). Pre-requisito del build: main
(gastos-multi-moneda) mergeado a la rama antes de T1.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec creada — 4 tareas, 9 test cases. Independiente de `gastos-multi-moneda`; dependencia de `importar-resumen-tarjeta` (build en ese orden). |
| 2 | 2026-09-15 | build | verified | pass | Merge de main (gastos-multi-moneda) pre-T1; T1-T4 implementadas por TDD; 223 pytest + 91 vitest en verde; migración 0011 idempotente contra Postgres real; smoke manual en vivo confirma el Outcome (banner en Inicio). |
