# Verify — Crear tarea sin puntos crea una tarea de 0 puntos

## T1 — Enviar Puntos como ausente cuando el campo está vacío

### Test Scenarios
- Error: Nombre completo, Puntos vacío → error de negocio, ninguna tarea creada (TC-001).
- Happy path: Nombre y Puntos completos → tarea creada normalmente (TC-002).

### Gate Criteria
- `[AUTO]` TC-001, TC-002 en verde.
- `[AUTO]` `npm run build` sin errores de tipos.
- `[AUTO]` Suite completa de `npm run test -- --run` sigue en verde.

## End-to-End Verification
1. `npm run test -- --run` y `npm run build` en verde.
2. Smoke manual: intentar crear una tarea sin puntos en el docker-compose local → error visible, sin tarea nueva en el listado.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001 | ¿El body real enviado tiene la clave `puntos` ausente, o `puntos: 0`? | La condición de vacío compara contra el valor equivocado (ej. `!puntos` en vez de `puntos === ""`, que trataría `"0"` como vacío incorrectamente) |
| TC-002 | ¿`Number(puntos)` sigue aplicándose cuando el campo SÍ tiene contenido? | La condición invertida, enviando `undefined` también en el caso con valor |
