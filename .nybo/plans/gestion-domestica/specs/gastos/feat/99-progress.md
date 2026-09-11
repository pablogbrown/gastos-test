# Progress — Gestión de Gastos

## Checklist

### Tasks
- [ ] T1 — Data Layer: Gasto, Categoría y Participantes
- [ ] T2 — Service Layer: Registro, División y Balance
- [ ] T3 — API Routes: Gastos y Balance
- [ ] T4 — UI: Registro de Gasto, Balance e Historial

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[UNIT]* — Registrar gasto con datos válidos
- [ ] `[TC-002]` *[UNIT]* — Gasto sin categoría es rechazado
- [ ] `[TC-003]` *[UNIT]* — No-admin no puede crear categoría
- [ ] `[TC-004]` *[UNIT]* — Gasto sin participantes explícitos se divide entre todos los activos
- [ ] `[TC-005]` *[UNIT]* — Gasto con participantes explícitos solo los afecta a ellos
- [ ] `[TC-006]` *[UNIT]* — División de $40.000 entre 4 participantes da $10.000 c/u
- [ ] `[TC-007]` *[UNIT]* — Balance calculado según el ejemplo del documento
- [ ] `[TC-008]` *[UNIT]* — Transferencia sugerida entre deudor y acreedor
- [ ] `[TC-009]` *[INTEGRATION]* — Nuevo miembro no altera gastos previos
- [ ] `[TC-010]` *[INTEGRATION]* — Historial incluye gastos de miembros desactivados

## Completion Summary
Not yet started.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 10 test cases. |
