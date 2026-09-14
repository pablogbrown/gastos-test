# T2 — `App.tsx` resuelve el rol real del Usuario

## Scope
- `src/frontend/api/casasClient.ts` — `Miembro`: agregar `usuario_id: string | null`.
- `src/frontend/App.tsx` — reemplazar `rolUsuarioActual="admin"` hardcodeado por un valor resuelto.
- `tests/unit/frontend/App.test.tsx` — TC-002, TC-003, TC-004.

## Changes
**UI**
- `casasClient.ts`: `Miembro` interface — agregar `usuario_id: string |
  null` (mismo tipo que el resto de los ids, `string`, no `UUID` en
  TypeScript).
- `App.tsx`: agregar
  ```ts
  const usuarioIdActual = obtenerUsuarioIdActual();
  const miMiembro = miembros.find((m) => m.usuario_id === usuarioIdActual);
  const rolUsuarioActual: Rol = miMiembro?.rol ?? "member";
  ```
  y usar `rolUsuarioActual` (en vez del literal `"admin"`) en las dos
  invocaciones: `<Miembros ... rolUsuarioActual={rolUsuarioActual} />`,
  `<Tareas ... rolUsuarioActual={rolUsuarioActual} />`.

## Design Rationale
Deriva el rol de un dato ya cargado (`miembros`) más un dato ya
disponible (`obtenerUsuarioIdActual()`, ya usado en este mismo
componente) — no agrega estado nuevo ni un request adicional. El
fallback `?? "member"` es una decisión de seguridad explícita (spec
REQ-002): mientras `miembros` carga o en cualquier estado inconsistente,
nunca se asume `"admin"`.

## Dependencies
T1 — necesita que `usuario_id` viaje en la respuesta de
`listarMiembros` para poder cruzarlo.

## Done When
- [ ] TC-002, TC-003, TC-004 pasan.
- [ ] `npm run build` sin errores de tipos.
- [ ] `npm run test -- --run` completo sigue en verde.

## Interfaces Produced
Ninguna nueva — extiende una interfaz ya exportada (`Miembro`) y cambia
el valor interno de una prop ya existente.

## Standalone Verifiable
Sí — TC-002/003/004 renderizan `App` con una lista de `miembros`
mockeada que incluye `usuario_id`, sin depender de T3.
