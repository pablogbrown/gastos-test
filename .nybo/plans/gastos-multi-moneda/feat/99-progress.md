# Progress — Multi-moneda en gastos, cuotas y suscripciones

## Checklist

### Tasks
- [x] T1 — `Gasto`/`Suscripcion` guardan `moneda`; migración
- [x] T2 — Servicios propagan y separan por moneda
- [x] T3 — API expone `moneda`
- [ ] T4 — Selector de moneda; Balance por secciones

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Gasto en USD persiste correctamente
- [ ] `[TC-002]` *[INTEGRATION]* — Sin moneda, default ARS (control)
- [ ] `[TC-003]` *[INTEGRATION]* — Balance separado por moneda con actividad en ambas
- [ ] `[TC-004]` *[UNIT]* — Sin actividad en USD, ninguna fila USD
- [ ] `[TC-005]` *[UNIT]* — Transferencias nunca cruzan moneda
- [ ] `[TC-006]` *[INTEGRATION]* — Suscripción en USD genera gasto en USD
- [ ] `[TC-007]` *[INTEGRATION]* — Cuotas mantienen la misma moneda
- [ ] `[TC-008]` *[INTEGRATION]* — Moneda inválida rechazada con 400
- [ ] `[TC-009]` *[UNIT]* — Formulario envía `moneda` en el body
- [ ] `[TC-010]` *[UNIT]* — Balance renderiza secciones separadas sin total combinado

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec creada — 4 tareas, 10 test cases. Foundation para `tarjetas-credito` e `importar-resumen-tarjeta` (build en ese orden). |
