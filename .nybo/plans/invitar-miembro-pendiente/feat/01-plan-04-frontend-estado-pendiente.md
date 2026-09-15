# T4 — `Miembros.tsx` muestra "Pendiente"

## Scope
- `src/frontend/pages/Miembros.tsx`.
- `src/frontend/api/casasClient.ts` — `Miembro` ya tiene `usuario_id` (spec `resolver-rol-usuario-en-casa`), no requiere cambio de tipo.
- `tests/unit/frontend/Miembros.test.tsx` — TC-007, TC-008.

## Changes
**UI**
- En la tabla de Miembros, la celda "Estado" muestra:
  - `usuario_id == null` → `Chip` "Pendiente" (color `warning`, mismo
    patrón visual que el `Chip` de estado ya existente).
  - `usuario_id != null && activo` → "Activo" (sin cambio).
  - `usuario_id != null && !activo` → "Inactivo" (sin cambio).
- La acción "Desactivar" no se muestra para una fila pendiente
  (`usuario_id == null`) — no tiene sentido desactivar algo que nunca
  se activó, y `desactivar_miembro` tampoco fue diseñado para ese caso.
- El helper text del campo Email ("Debe ser un email ya registrado",
  agregado en `fix/miembros-tareas-integration-gaps`) se actualiza a
  algo como "Si la persona no está registrada, queda invitada hasta que
  se registre con este email" — ya no es cierto que deba estar
  registrada.

## Design Rationale
Reutiliza el `Chip` ya existente en la misma tabla en vez de introducir
un componente nuevo — solo cambia qué condición determina label/color.

## Dependencies
T2 — necesita que el backend realmente pueda devolver una fila con
`usuario_id: null` desde un alta exitosa (antes de T2, ese caso no era
alcanzable en la práctica).

## Done When
- [ ] TC-007, TC-008 pasan.
- [ ] `npm run build` sin errores de tipos.
- [ ] `npm run test -- --run` completo sigue en verde.

## Interfaces Produced
Ninguna nueva.

## Standalone Verifiable
Sí — TC-007/008 renderizan `Miembros` con una lista mockeada que incluye
una fila con `usuario_id: null`.
