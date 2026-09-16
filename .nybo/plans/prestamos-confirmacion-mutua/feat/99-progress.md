# Progress — Confirmación mutua de un préstamo

## Checklist

### Tasks
- [ ] T1 — `Prestamo` guarda confirmación por rol; migración
- [ ] T2 — Auto-confirmación al crear; `confirmar_prestamo`; guard en el cambio de estado
- [ ] T3 — API expone confirmación; endpoint de confirmar/rechazar
- [ ] T4 — `Prestamos.tsx` muestra el estado y las acciones de confirmación

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Prestamista registra, su rol queda confirmado
- [ ] `[TC-002]` *[INTEGRATION]* — Deudor registra, su rol queda confirmado
- [ ] `[TC-003]` *[INTEGRATION]* — Tercero registra, ambos pendientes
- [ ] `[TC-004]` *[INTEGRATION]* — Tercero no puede confirmar/rechazar
- [ ] `[TC-005]` *[INTEGRATION]* — Ambas partes confirman → confirmado
- [ ] `[TC-006]` *[INTEGRATION]* — Una parte rechaza → rechazado permanente
- [ ] `[TC-007]` *[INTEGRATION]* — No se puede cambiar pagado/pendiente antes de confirmar
- [ ] `[TC-008]` *[UNIT]* — Visible para toda la casa como "pendiente de confirmación"
- [ ] `[TC-009]` *[UNIT]* — Solo la parte pendiente ve los botones de confirmar/rechazar

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 9 test cases. Depende de `prestamos-entre-miembros` (ya shippeada y mergeada). |
