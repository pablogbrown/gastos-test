# Progress — Préstamos entre miembros

## Checklist

### Tasks
- [x] T1 — Modelo `Prestamo` + migración
- [x] T2 — `prestamo_service` (alta/listado/estado)
- [x] T3 — Rutas de préstamos
- [x] T4 — Pantalla "Préstamos"; entrada de navegación

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Alta de préstamo con datos válidos
- [x] `[TC-002]` *[INTEGRATION]* — Prestamista igual a deudor rechazado
- [x] `[TC-003]` *[INTEGRATION]* — Moneda inválida rechazada
- [x] `[TC-004]` *[INTEGRATION]* — Cambio de estado en ambos sentidos
- [x] `[TC-005]` *[INTEGRATION]* — Listado ordenado por fecha descendente
- [x] `[TC-006]` *[INTEGRATION]* — No afecta Balance (control)
- [x] `[TC-007]` *[UNIT]* — Alta desde el formulario de la pantalla
- [x] `[TC-008]` *[UNIT]* — Chip clickeable cambia el estado

## Completion Summary
4 tareas implementadas (T1-T4), TC-001 a TC-008 en verde. Suite completa:
281 pytest passed (1 skipped, esperado — requiere `DATABASE_URL` externa
de docker-compose) + 108 vitest passed. `npm run build`/`npm run lint`
sin errores. Migración `0014_prestamos` verificada idempotente (2 y 3
pasadas) contra Postgres real vía contenedor Docker efímero.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 8 test cases. Independiente de `gastos-sin-reparto` (sin dependencia funcional). |
| 2 | 2026-09-16 | build | verified | pass | T1-T4 implementados vía TDD. Suite completa en verde (281 pytest + 108 vitest), build/lint limpios, migración 0014 idempotente contra Postgres real (Docker). |
