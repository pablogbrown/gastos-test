# Verify — Altas y bajas de miembro no quedan en el Historial

## T1 — Registrar actividad en alta y baja de miembro

### Test Scenarios
- Happy path: agregar un miembro → aparece `miembro_agregado` en el historial (TC-001).
- Happy path: desactivar un miembro → aparece `miembro_desactivado` en el historial (TC-002).
- Error: un intento fallido (email no registrado, actor no-admin) no agrega ninguna entrada (TC-003).

### Gate Criteria
- `[AUTO]` TC-001, TC-002, TC-003 en verde.
- `[AUTO]` Suite completa de `pytest tests/` sigue en verde.

## T2 — Frontend reconoce el nuevo tipo

### Test Scenarios
- Render de una entrada `miembro_desactivado` mockeada → ícono y etiqueta correctos, sin excepción (TC-004).

### Gate Criteria
- `[AUTO]` TC-004 en verde.
- `[AUTO]` `npm run build` sin errores de tipos.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. `npm run build` sin errores.
3. Smoke manual contra el docker-compose local: agregar un miembro,
   desactivarlo, abrir "Actividad" → ambas acciones aparecen en orden
   cronológico correcto, con etiquetas legibles.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001/TC-002 | ¿Se llama `registrar_actividad` DESPUÉS del `commit`, no antes? | Llamada movida antes de la confirmación de la transacción, o dentro del bloque `try` equivocado |
| TC-003 | ¿La llamada a `registrar_actividad` quedó fuera de la ruta de éxito? | Se llama incluso cuando `ValidationError`/`PermissionDeniedError`/`NotFoundError` se lanza antes |
| TC-004 | ¿`ETIQUETAS_TIPO` y `ICONOS_TIPO` tienen AMBOS la entrada nueva? | Solo uno de los dos `Record` actualizado — el compilador debería atraparlo, revisar que no se usó `as any` |
