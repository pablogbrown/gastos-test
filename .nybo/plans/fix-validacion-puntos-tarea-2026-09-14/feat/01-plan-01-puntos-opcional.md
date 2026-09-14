# T1 — Enviar Puntos como ausente cuando el campo está vacío

## Scope
- `src/frontend/api/tareasClient.ts` — `CrearTareaInput.puntos`: `number` → `number | undefined`.
- `src/frontend/pages/Tareas.tsx` — `handleCrear`: construir `puntos` condicionalmente.
- `tests/unit/frontend/Tareas.test.tsx` — TC-001, TC-002.

## Changes
**UI**
- `tareasClient.ts`: `CrearTareaInput.puntos: number` → `puntos?: number`.
- `Tareas.tsx`'s `handleCrear`: reemplazar `puntos: Number(puntos)` por
  `puntos: puntos === "" ? undefined : Number(puntos)`.

## Design Rationale
Cambio mínimo y localizado: no se agrega validación duplicada en el
cliente (`required`, mensajes propios) porque la regla de negocio ya
vive correctamente en el backend y ya se muestra vía el `Alert` de
error existente (`esApiError(err) ? err.detail : ...`) — el fix solo
deja de enmascarar "ausente" como "cero" antes de que esa regla pueda
evaluarlo.

## Dependencies
Ninguna.

## Done When
- [ ] TC-001, TC-002 pasan.
- [ ] `npm run build` sin errores de tipos.
- [ ] `npm run test -- --run` completo sigue en verde.

## Interfaces Produced
Ninguna nueva — solo relaja el tipo de un campo ya exportado
(`CrearTareaInput.puntos`).

## Standalone Verifiable
Sí — TC-001/002 verifican el comportamiento completo del formulario sin
depender de otros fixes.
