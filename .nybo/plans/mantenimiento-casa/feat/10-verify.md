# Verify — Mantenimiento de la casa

## T1 — Modelos

### Gate Criteria
- `[AUTO]` Suite completa en verde con los modelos nuevos.
- `[AUTO]` Migración idempotente contra Postgres real.

## T2 — `mantenimiento_service`

### Test Scenarios
- Alta válida (TC-001); recurrente sin periodicidad/fecha rechazado (TC-002).
- Materiales al crear (TC-003); marcar conseguido (TC-004).
- Completar no-recurrente sin generar nueva instancia (TC-005); recurrente genera la siguiente con la fecha correcta (TC-006); completar antes de tiempo rechazado (TC-007).
- Alerta a 5 días aparece, a 20 días no (TC-008).

### Gate Criteria
- `[AUTO]` TC-001 a TC-008 en verde.

## T3 — API + dashboard

### Gate Criteria
- `[AUTO]` `pytest tests/` completo sigue en verde.
- `[AUTO]` `GET .../dashboard` incluye `mantenimientoConAlerta`.

## T4 — Frontend

### Gate Criteria
- `[AUTO]` TC-009 y TC-010 en verde.
- `[AUTO]` `npm run build`/`npm run lint` sin errores.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra docker-compose: crear un ítem recurrente con
   fecha estimada próxima → completar → aparece la nueva instancia
   pendiente, no completable hoy; con fecha a ≤7 días, aparece el banner
   en Inicio.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-006 | ¿`_DIAS_POR_PERIODICIDAD["mensual"]` usa 30 días fijos (no aritmética de mes calendario)? | Confirmar que la spec usa días fijos, no `_sumar_meses` — está documentado así en `00-overview.md`, no es un bug si difiere de `tarea_service` |
| TC-007 | ¿El gate compara `date.today() < fecha_estimada`, mismo operador que el ya corregido en `tarea_service`? | Copiar el criterio exacto (>= permite completar el mismo día) |
| Nav (T4) | ¿El TC-001 de `nav-agrupada` (`AppShell.test.tsx`) sigue esperando "Tareas" como entrada suelta? | Ese test necesita actualizarse al nuevo grupo, mismo criterio que `nav-agrupada` ya usó para su propio TC-002 |
