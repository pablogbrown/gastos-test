# Resolver el rol real del Usuario autenticado en la casa actual

## Intention

### What
`App.tsx` pasa `rolUsuarioActual="admin"` hardcodeado a `<Miembros>` y a
`<Tareas>` para todo Usuario autenticado, sin importar su rol real
(`admin`/`member`) en la casa elegida. Esta feature agrega la capacidad
de resolver ese rol de verdad, del lado del cliente, a partir de la
sesión JWT ya existente.

### Why
Con el rol hardcodeado en `"admin"`, cualquier miembro ve controles
("Agregar miembro", "Desactivar", "Marcar completada" en cualquier
tarea) que el backend después rechaza — una UI que miente sobre lo que
el usuario puede hacer. Además enmascara un bug relacionado en
`Tareas.tsx`: `puedeCompletar()` compara el id global del Usuario contra
`tarea.responsableId` (un id de Miembro, por-casa) — dos identidades
distintas por diseño desde `usuarios-auth` — que nunca coinciden salvo
casualidad, silenciado hoy porque el chequeo de rol `"admin"` siempre
gana primero.

## Solution
El backend expone `usuario_id` en `MiembroOut` (ya lo tiene internamente
— hoy no viaja en la respuesta). El frontend cruza ese campo contra el
`sub` del JWT propio (`obtenerUsuarioIdActual()`) sobre la lista de
miembros de la casa ya cargada en `App.tsx`, para resolver tanto "mi rol
real" como "mi propio Miembro.id en esta casa" — este último reemplaza
la comparación rota de `puedeCompletar()`. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Un usuario con rol `member` deja de ver "Agregar miembro"/"Desactivar",
y "Marcar completada" aparece exactamente para quien la spec original
de `tareas-puntos` definió (el responsable asignado, cualquiera si no
hay responsable, o un Administrador) — usando la identidad de Miembro
correcta, no la global.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | La respuesta de `MiembroOut` incluye el `usuario_id` de cada miembro. | Es un dato ya persistido (FK existente) que ningún miembro de la casa consideraría privado respecto a otro miembro — no introduce un dato nuevo a proteger. |
| REQ-002 | `App.tsx` resuelve el rol real del Usuario autenticado en la casa elegida, cruzando el `usuario_id` de la lista de miembros contra el `sub` del JWT propio, y lo pasa a `<Miembros>`/`<Tareas>` en vez del valor hardcodeado. | Si el cruce no encuentra ninguna fila (estado inconsistente/carga en curso), el rol resuelto es `"member"` — nunca `"admin"` por default, para no reabrir el mismo problema con un fallback inseguro. |
| REQ-003 | `Tareas.tsx` resuelve "¿soy yo el responsable de esta tarea?" comparando el `Miembro.id` propio en esta casa (no el `Usuario.id` global) contra `tarea.responsableId`. | Mismo criterio de REQ-002 para resolver el Miembro propio; reemplaza la comparación existente en `puedeCompletar()`, sin cambiar las reglas de visibilidad ya definidas (responsable asignado, cualquiera si no hay responsable, o Administrador). |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** una casa con 2 miembros **When** se llama `GET /casas/{id}/miembros` **Then** cada objeto de la respuesta incluye `usuario_id` | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** un Usuario cuyo `Miembro` en la casa elegida tiene `rol: "member"` **When** `App.tsx` resuelve el rol y renderiza `Miembros` **Then** no se muestran "Agregar miembro" ni "Desactivar" | `[UNIT]` |
| TC-003 (REQ-002) | **Given** un Usuario cuyo `Miembro` en la casa elegida tiene `rol: "admin"` **When** `App.tsx` resuelve el rol **Then** `Miembros`/`Tareas` reciben `rolUsuarioActual: "admin"` y muestran los controles correspondientes | `[UNIT]` |
| TC-004 (REQ-002) | **Given** la lista de miembros todavía no incluye ninguna fila cuyo `usuario_id` coincida con el Usuario autenticado (ej. está cargando) **When** se renderiza el shell **Then** el rol resuelto es `"member"`, nunca `"admin"` | `[UNIT]` |
| TC-005 (REQ-003) | **Given** una tarea con `responsableId` igual al `Miembro.id` propio del Usuario en esta casa **When** ese Usuario ve el listado de tareas **Then** el botón "Marcar completada" aparece para esa tarea | `[UNIT]` |
| TC-006 (REQ-003) | **Given** una tarea con `responsableId` igual al `Miembro.id` de OTRO usuario en esta casa, y el Usuario actual tiene rol `member` **When** ese Usuario ve el listado de tareas **Then** el botón "Marcar completada" NO aparece para esa tarea | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | QA manual profunda del entorno local dockerizado tras shippear `usuarios-auth` — 2026-09-14. |
| Spec | usuarios-auth (specs/auth-frontend) | .nybo/plans/usuarios-auth/specs/auth-frontend/spec.md |
