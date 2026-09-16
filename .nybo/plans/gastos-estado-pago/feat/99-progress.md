# Progress — Estado de pago de un gasto

## Checklist

### Tasks
- [x] T1 — `Gasto` guarda `estado`; migración
- [x] T2 — Servicios propagan `estado`; `actualizar_estado_gasto`
- [x] T3 — API expone `estado`; endpoint de actualización
- [x] T4 — Selector en el formulario; chip clickeable en el listado

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Sin estado, default "pagado"
- [x] `[TC-002]` *[INTEGRATION]* — Con estado="a_pagar", persiste así
- [x] `[TC-003]` *[INTEGRATION]* — Cuotas heredan el mismo estado
- [x] `[TC-004]` *[INTEGRATION]* — Gasto de suscripción nace "a_pagar"
- [x] `[TC-005]` *[INTEGRATION]* — Gastos importados nacen "a_pagar"
- [x] `[TC-006]` *[INTEGRATION]* — Actualizar estado en ambos sentidos
- [x] `[TC-007]` *[INTEGRATION]* — Estado inválido rechazado con 400
- [x] `[TC-008]` *[INTEGRATION]* — Cambiar estado no afecta Balance
- [x] `[TC-009]` *[UNIT]* — Formulario envía estado en el body
- [x] `[TC-010]` *[UNIT]* — Chip clickeable actualiza el estado

#### Outcome Smoke Test
- [x] Observado en vivo (docker-compose real, stack ya levantado + `make migrate`): importar/crear gastos sin `estado` → "pagado"; con `estado="a_pagar"` → persiste así; `PATCH` cambia el estado en ambos sentidos y la UI (`http://localhost:5173`) refleja el chip verde/naranja correspondiente sin recargar; `GET /balance` antes/después del cambio de estado devuelve montos idénticos. Ver `evidence/1/build-results.md`'s sección Live evidence y captura `evidence/1/screenshots/gastos-estado-selector-y-chips.jpg`.

## Completion Summary
Las 4 tareas se implementaron siguiendo TDD (Red→Green→Refactor) por tarea. `estado` sigue exactamente el mismo patrón ya establecido para `moneda`/`tarjeta_id` en `Gasto` (columna `String` simple sin enum nativo, constante de validación en `gasto_service.py`, propagación explícita en cada generador automático). Suite completa verde (260 backend + 97 frontend), migración `0013_gasto_estado` verificada idempotente contra Postgres real vía Docker, y el flujo completo (creación → import → PATCH → Balance sin cambios) confirmado en vivo contra el stack de docker-compose. Convenciones `[SERVP-05]`/`[FRONP-01]` agregadas a memoria del proyecto.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 10 test cases. Independiente de `gastos-vista-mensual` y `nav-agrupada` (se pueden buildear en cualquier orden entre sí). |
| 2 | 2026-09-16 | build | verified | observed | T1-T4 implementadas, 10/10 test cases en verde, migración idempotente contra Postgres real, smoke en vivo contra docker-compose (API + UI) confirmado. `status: ready`. |
