# Invitar a un miembro que todavía no tiene cuenta

## Intention

### What
Un Administrador puede agregar como miembro a alguien por su email
aunque esa persona todavía no se haya registrado en la app. La
membresía queda en estado "pendiente" y se vincula automáticamente en
cuanto esa persona se registra con ese mismo email — sin enviar ningún
email ni requerir un paso extra de la persona invitada.

### Why
Hoy `agregar_miembro` exige que el email ya corresponda a un Usuario
registrado, con un mensaje "No existe un Usuario registrado con el
email...". En la práctica nadie se registra en una app antes de que lo
inviten — el caso de uso real es al revés: el Administrador invita
primero, la persona se entera y se registra después. El flujo actual
bloquea exactamente ese caso.

## Solution
`agregar_miembro` ya no rechaza un email sin Usuario registrado — crea
una fila `Miembro` "pendiente" (sin `usuario_id`, guardando el email
invitado). `registrar_usuario` (spec `usuarios-auth`), al crear un
Usuario nuevo, busca membresías pendientes con ese mismo email y las
vincula automáticamente. La UI de Miembros distingue "Pendiente" de
Activo/Inactivo. Ver **[Solution Overview](feat/00-overview.md)**.

## Outcome
Un Administrador invita a alguien por email sin que esa persona tenga
que registrarse primero. Cuando esa persona se registra (con el mismo
email, en cualquier momento posterior), pasa a ser miembro activo de
todas las casas donde la invitaron, sin ninguna acción manual adicional
de nadie.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Cuando un Administrador agrega un miembro con un email que no corresponde a ningún Usuario registrado, el sistema crea la membresía en estado pendiente (sin `usuario_id`) en vez de rechazar la operación. | El email invitado se guarda normalizado (recortado, minúsculas) para poder matchearlo después. |
| REQ-002 | Cuando un Usuario se registra con un email que coincide con una o más membresías pendientes, el sistema las vincula automáticamente (les asigna su `usuario_id`) como parte del registro, sin acción adicional de nadie. | Vincula TODAS las pendientes con ese email, en cualquier casa — un mismo Usuario puede tener membresías pendientes en varias casas a la vez. |
| REQ-003 | Un Administrador no puede crear una segunda invitación pendiente para el mismo email en la misma casa mientras la primera siga sin vincularse. | Rechazo por el mismo criterio de "ya es miembro de esta casa" que ya existe para un Usuario registrado — evita duplicados hasta que se vincule. |
| REQ-004 | La pantalla de Miembros muestra un estado "Pendiente" distintivo para una membresía todavía no vinculada a un Usuario, distinto de Activo/Inactivo. | Una fila pendiente no puede desactivarse (no tiene sentido desactivar algo que nunca se activó) — la acción "Desactivar" no se muestra para ella. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un email sin ningún Usuario registrado **When** un Administrador agrega un miembro con ese email **Then** la API responde 201 con una fila Miembro sin `usuario_id` | `[INTEGRATION]` |
| TC-002 (REQ-001, control) | **Given** un email que ya corresponde a un Usuario registrado **When** un Administrador agrega un miembro con ese email **Then** la vinculación es inmediata (`usuario_id` seteado desde el alta), igual que hoy | `[INTEGRATION]` |
| TC-003 (REQ-002) | **Given** una membresía pendiente para el email `x@example.com` en la casa A **When** alguien se registra con `x@example.com` **Then** esa membresía queda con `usuario_id` seteado al Usuario recién creado | `[INTEGRATION]` |
| TC-004 (REQ-002) | **Given** membresías pendientes para `x@example.com` en las casas A y B **When** esa persona se registra **Then** ambas membresías quedan vinculadas | `[INTEGRATION]` |
| TC-005 (REQ-002, control) | **Given** un email sin ninguna membresía pendiente **When** alguien se registra con ese email **Then** el registro funciona exactamente igual que hoy, sin vincular nada | `[UNIT]` |
| TC-006 (REQ-003) | **Given** una invitación pendiente ya creada para `x@example.com` en la casa A **When** un Administrador intenta invitar a `x@example.com` de nuevo en la casa A **Then** la API responde 400 | `[INTEGRATION]` |
| TC-007 (REQ-004) | **Given** una fila de Miembros con `usuario_id` nulo **When** se renderiza la pantalla Miembros **Then** se muestra un estado "Pendiente" y no se ofrece la acción "Desactivar" para esa fila | `[UNIT]` |
| TC-008 (REQ-004, control) | **Given** una fila de Miembros ya vinculada (`usuario_id` no nulo) **When** se renderiza la pantalla Miembros **Then** sigue mostrando Activo/Inactivo y "Desactivar" exactamente como hoy | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario reportó, con una captura de la pantalla Miembros, que agregar a alguien no registrado responde "No existe un Usuario registrado con el email..." y pidió que ese caso funcione como invitación en vez de rechazo — 2026-09-15. Confirmado vía pregunta de aclaración: alta pendiente + auto-vinculación al registrarse, sin envío de emails. |
| Spec | usuarios-auth (specs/auth-backend) | .nybo/plans/usuarios-auth/specs/auth-backend/spec.md |
