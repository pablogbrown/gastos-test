# Task 4 — Adaptar tests existentes y documentación

## Scope
- `tests/unit/frontend/*.test.tsx` — cualquier test que mockeaba `usuarioId`/`X-Usuario-Id`.
- `README.md` — sección de login/registro.

## Changes
### Frontend — Tests + Docs
- Adaptar los tests de frontend existentes (de `ui-modernization` y las specs de `gestion-domestica`) que asumían un `usuarioId` pasado directamente a cada pantalla, para en cambio pasar por el nuevo flujo de sesión (mock de `authClient.obtenerToken()`), sin cambiar qué comportamiento verifican.
- `README.md`: documentar el flujo de registro/login y que `X-Usuario-Id` ya no existe.

## Design Rationale
Igual que en `ui-modernization` T4: separar "cambiar el comportamiento" de "confirmar que nada se rompió" en su propia task final.

## Dependencies
T3 (todo el flujo de auth debe existir para adaptar los tests contra él).

## Done When
- [ ] TC-007 pasa.
- [ ] `npm run test` completo en verde.
- [ ] README actualizado.

## Interfaces Produced
Ninguno (task final de la spec).

## Standalone Verifiable
No en aislamiento — depende de T1, T2 y T3 completas.
