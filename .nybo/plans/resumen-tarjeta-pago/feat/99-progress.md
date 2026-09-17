# Progress — resumen-tarjeta-pago

## Checklist

### Tasks
- [x] T1 — `ResumenTarjeta`; `Gasto.resumen_id`; migración `0019`
- [x] T2 — Tracking de resúmenes; `pagar_resumen`; threading `resumen_id`
- [x] T3 — Endpoints de resúmenes; 409 en importar duplicado
- [ ] T4 — UI de resúmenes en Tarjetas.tsx

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Importar un resumen crea ResumenTarjeta
- [x] `[TC-002]` *[INTEGRATION]* — Importar duplicado se rechaza (409)
- [x] `[TC-003]` *[INTEGRATION]* — Gastos creados quedan vinculados al resumen
- [x] `[TC-004]` *[INTEGRATION]* — Pagar resumen marca todo como pagado
- [x] `[TC-005]` *[INTEGRATION]* — Pagar resumen no afecta otros/doble pago
- [x] `[TC-006]` *[INTEGRATION]* — Listar resúmenes de una tarjeta
- [ ] `[TC-007]` *[UNIT]* — UI muestra resúmenes + botón Pagar resumen
- [ ] `[TC-008]` *[UNIT]* — UI muestra error claro en importación duplicada

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-17 | plan | — | — | Spec creada — 4 tareas, 8 test cases. Reportado en vivo sobre `importar-resumen-tarjeta` ya shippeada: tracking de resúmenes + prevención de duplicados + pago masivo. |
| 2 | 2026-09-17 | build | — | — | T1 listo: modelo `ResumenTarjeta`, `Gasto.resumen_id` (columna plana, sin FK a nivel de modelo), migración `0019_resumen_tarjeta`. Suite completa en verde (349 tests) contra Postgres real vía `docker compose exec backend pytest`. |
| 3 | 2026-09-17 | build | — | — | T2 listo: TC-001 a TC-006 en verde (`resumen_tarjeta.test.py`, 9 tests). `importar_resumen` rechaza duplicado `(tarjeta_id, fecha_cierre)` antes de tocar la tarjeta; threading de `resumen_id` en las 3 rutas de creación de gasto; `pagar_resumen`/`listar_resumenes` nuevos. Desviación registrada: 3 tests preexistentes (`resumen_importer.test.py`, `gasto_estado.test.py`, `importar_resumen_routes.test.py`) necesitaron su fixture extendida (migración `0019` + monkeypatch de `resumen_importer_service.get_session`, antes innecesario) — el plan asumía "sin modificaciones", pero `resumen_importer_service` ahora abre su propia sesión para el chequeo de duplicado. Un cuarto test (`test_tc006_...reutiliza`) reimportaba el mismo PDF dos veces para probar reutilización de suscripción — ese path ahora choca con el guard REQ-002 nuevo (mismo patrón que [SERVP-07]); se varió el cierre de la segunda importación en vez de relajar el guard. Suite completa en verde (358 tests).|
| 4 | 2026-09-17 | build | — | — | T3 listo: `GET .../tarjetas/{id}/resumenes` y `PATCH .../resumenes/{id}/pagar` nuevos; `ConflictError` -> 409 en `POST .../resumen`; `ResumenImportadoOut.resumen_id` agregado. `tarjetas_routes.test.py` extendido (13 tests, 5 nuevos) ejercitando el flujo real end-to-end (`multipart/form-data`) en vez de solo mockear el service layer. Suite completa en verde (363 tests). |
