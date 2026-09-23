# T1 — Login + Registro

## Scope
- `src/frontend/pages/Login.tsx`
- `src/frontend/pages/Registro.tsx`

## Changes
- Layout: tarjeta (`Card`) centrada vertical y horizontalmente, fondo del tema detrás (no un formulario a ancho completo pegado arriba).
- Encabezado de marca: "taskia" en tipografía destacada (usa la escala tipográfica de `sistema-visual`), sin agregar ningún logo/imagen (fuera de scope).
- Campos, botones y mensajes de error/validación existentes preservados exactamente — solo restyled bajo el nuevo tema.
- Link cruzado Login↔Registro preservado.

## Implementation Steps
1. Baseline: confirmar `Login.test.tsx`/`Registro.test.tsx` en verde.
2. Envolver el formulario existente en una tarjeta centrada.
3. Agregar el encabezado de marca "taskia".
4. Confirmar que ningún mensaje de error cambió de texto ni de rol accesible.
5. Re-correr ambos suites sin modificar queries.

## Design Rationale
Un layout de tarjeta centrada es el patrón estándar para pantallas de autenticación (foco único, sin distracción de navegación) — coherente con que estas pantallas son el único momento en que el usuario ve la app sin el shell de navegación completo.

## Dependencies
Ninguna dentro de esta spec — consume el tema de `sistema-visual`.

## Done When
- [ ] TC-001, TC-002, TC-004 pasan (para estas dos pantallas).
- [ ] `Login.test.tsx` y `Registro.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí.
