# Progress — Préstamos entre miembros

## Checklist

### Tasks
- [ ] T1 — Modelo `Prestamo` + migración
- [ ] T2 — `prestamo_service` (alta/listado/estado)
- [ ] T3 — Rutas de préstamos
- [ ] T4 — Pantalla "Préstamos"; entrada de navegación

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Alta de préstamo con datos válidos
- [ ] `[TC-002]` *[INTEGRATION]* — Prestamista igual a deudor rechazado
- [ ] `[TC-003]` *[INTEGRATION]* — Moneda inválida rechazada
- [ ] `[TC-004]` *[INTEGRATION]* — Cambio de estado en ambos sentidos
- [ ] `[TC-005]` *[INTEGRATION]* — Listado ordenado por fecha descendente
- [ ] `[TC-006]` *[INTEGRATION]* — No afecta Balance (control)
- [ ] `[TC-007]` *[UNIT]* — Alta desde el formulario de la pantalla
- [ ] `[TC-008]` *[UNIT]* — Chip clickeable cambia el estado

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 8 test cases. Independiente de `gastos-sin-reparto` (sin dependencia funcional). |
