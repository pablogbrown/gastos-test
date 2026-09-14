# Verify — Ranking y dashboard muestran UUIDs crudos

## T1 — Resolver nombre de miembro

### Test Scenarios
- Happy path: miembro presente en la lista recibida → se muestra el nombre (TC-001, TC-003).
- Edge: miembro NO presente en la lista recibida (ej. fue eliminado) → fallback al id crudo, sin romper el render (TC-002).

### Gate Criteria
- `[AUTO]` TC-001, TC-002, TC-003 en verde.
- `[AUTO]` `npm run build` sin errores de tipos (props nuevas correctamente tipadas en ambos componentes y en `App.tsx`).
- `[AUTO]` Suite completa de `npm run test -- --run` sigue en verde (57+ tests previos).

## End-to-End Verification
1. `npm run test -- --run` y `npm run build` en verde.
2. Smoke manual: completar una tarea, entrar a Ranking y a Inicio → ambos muestran el nombre del miembro, no un UUID.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001/TC-003 | ¿La prop `miembros` llega realmente poblada al componente en el test? | Mock de `miembros` vacío, o comparación de id por referencia distinta a string |
| TC-002 | ¿El fallback usa `??` (nullish) y no `||`? | Un nombre vacío `""` (falsy) caería al fallback con `||` cuando no debería |
