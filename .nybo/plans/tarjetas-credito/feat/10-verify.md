# Verify — Gestión de tarjetas de crédito y alerta de vencimiento

## T1 — Modelo `TarjetaCredito`

### Gate Criteria
- `[AUTO]` Suite completa en verde con el modelo nuevo.
- `[AUTO]` Migración idempotente contra Postgres real.

## T2 — `tarjeta_service`

### Test Scenarios
- Alta con datos válidos (TC-001) y sin banco → 400 (TC-002).
- Edición de vencimiento persiste (TC-003).
- Baja (soft-delete) saca la tarjeta del listado activo (TC-004).
- Vence en 3 días → aparece en alerta (TC-005); ya vencida → aparece marcada (TC-006); vence en 20 días → no aparece (TC-007).

### Gate Criteria
- `[AUTO]` TC-001 a TC-007 en verde.

## T3 — API + dashboard

### Gate Criteria
- `[AUTO]` `pytest tests/` completo sigue en verde.
- `[AUTO]` `GET .../dashboard` incluye `tarjetas_con_alerta`.

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-008 y TC-009 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual: registrar una tarjeta con vencimiento a 3 días desde
   hoy → recargar Inicio → aparece el banner de alerta.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-005/TC-006/TC-007 | ¿`UMBRAL_ALERTA_DIAS` se compara con `<=` o `<`? | Off-by-one en el límite de 7 días |
| TC-006 | ¿`vencida` se calcula como `dias_para_vencimiento < 0`, no `<= 0`? | El día mismo del vencimiento no debería marcarse como "ya vencida" |
| TC-008 | ¿`dashboard_service` realmente propaga `tarjetas_con_alerta` hasta `DashboardResponse`? | Campo agregado en el dataclass pero no en el schema Pydantic de la ruta |
