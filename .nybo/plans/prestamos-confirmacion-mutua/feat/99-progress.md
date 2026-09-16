# Progress — Confirmación mutua de un préstamo

## Checklist

### Tasks
- [x] T1 — `Prestamo` guarda confirmación por rol; migración
- [x] T2 — Auto-confirmación al crear; `confirmar_prestamo`; guard en el cambio de estado
- [x] T3 — API expone confirmación; endpoint de confirmar/rechazar
- [x] T4 — `Prestamos.tsx` muestra el estado y las acciones de confirmación

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Prestamista registra, su rol queda confirmado
- [x] `[TC-002]` *[INTEGRATION]* — Deudor registra, su rol queda confirmado
- [x] `[TC-003]` *[INTEGRATION]* — Tercero registra, ambos pendientes
- [x] `[TC-004]` *[INTEGRATION]* — Tercero no puede confirmar/rechazar
- [x] `[TC-005]` *[INTEGRATION]* — Ambas partes confirman → confirmado
- [x] `[TC-006]` *[INTEGRATION]* — Una parte rechaza → rechazado permanente
- [x] `[TC-007]` *[INTEGRATION]* — No se puede cambiar pagado/pendiente antes de confirmar
- [x] `[TC-008]` *[UNIT]* — Visible para toda la casa como "pendiente de confirmación"
- [x] `[TC-009]` *[UNIT]* — Solo la parte pendiente ve los botones de confirmar/rechazar

## Completion Summary
4 tareas implementadas (T1-T4), 9 test cases en verde (backend: `prestamo_confirmacion.test.py` +
`prestamos_confirmacion_routes.test.py`; frontend: `Prestamos.test.tsx`). Suite completa:
296 passed/1 skipped (pytest) + 113 passed (vitest). `npm run build`/`lint` sin errores. Migración
`0016_prestamo_confirmacion` verificada idempotente contra Postgres real (docker). Smoke manual
end-to-end (API + UI real) confirmado contra el stack docker-compose ya levantado — ver
`evidence/1/build-results.md`. Curate aplicó 2 convenciones nuevas: `services.md` `[SERVP-07]`,
`frontend.md` `[FRONP-02]`. Cero entradas en `decisions.yaml`.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 9 test cases. Depende de `prestamos-entre-miembros` (ya shippeada y mergeada). |
| 2 | 2026-09-16 | build | verified | pass | Ciclo 1: T1-T4 implementadas, TC-001 a TC-009 en verde, suite completa + build/lint OK, migración 0016 idempotente contra Postgres real (docker), smoke live (API+UI) confirmado. Curate: SERVP-07, FRONP-02. `status: ready`. |
