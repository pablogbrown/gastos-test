# Progress — Estado de pago de un gasto

## Checklist

### Tasks
- [ ] T1 — `Gasto` guarda `estado`; migración
- [ ] T2 — Servicios propagan `estado`; `actualizar_estado_gasto`
- [ ] T3 — API expone `estado`; endpoint de actualización
- [ ] T4 — Selector en el formulario; chip clickeable en el listado

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Sin estado, default "pagado"
- [ ] `[TC-002]` *[INTEGRATION]* — Con estado="a_pagar", persiste así
- [ ] `[TC-003]` *[INTEGRATION]* — Cuotas heredan el mismo estado
- [ ] `[TC-004]` *[INTEGRATION]* — Gasto de suscripción nace "a_pagar"
- [ ] `[TC-005]` *[INTEGRATION]* — Gastos importados nacen "a_pagar"
- [ ] `[TC-006]` *[INTEGRATION]* — Actualizar estado en ambos sentidos
- [ ] `[TC-007]` *[INTEGRATION]* — Estado inválido rechazado con 400
- [ ] `[TC-008]` *[INTEGRATION]* — Cambiar estado no afecta Balance
- [ ] `[TC-009]` *[UNIT]* — Formulario envía estado en el body
- [ ] `[TC-010]` *[UNIT]* — Chip clickeable actualiza el estado

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 10 test cases. Independiente de `gastos-vista-mensual` y `nav-agrupada` (se pueden buildear en cualquier orden entre sí). |
