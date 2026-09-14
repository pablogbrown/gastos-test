# Fix — Membresía duplicada crashea la resolución de actor

## Intention

### What
`agregar_miembro` no valida que el Usuario (por email) ya tenga una fila
`Miembro` activa en esa casa — solo valida `identificacion` duplicada.
Si el mismo Usuario termina con 2+ filas `Miembro` activas en la misma
casa, **todo request autenticado de ese usuario a esa casa crashea con
500** (`sqlalchemy.exc.MultipleResultsFound` en
`resolver_actor_en_casa`, confirmado con traceback completo en logs).
Separadamente, durante la misma sesión de pruebas manuales, un miembro
con rol `member` logró desactivar al Administrador de la casa (PATCH
devolvió 200 en vez del 403 esperado) — un posible bypass de
autorización que no se pudo reproducir de forma aislada vía curl, pero
ocurrió inmediatamente después de un crash 500 de este mismo tipo en la
misma sesión.

### Why
Un 500 no manejado rompe la casa entera para ese usuario sin recuperación
posible desde la UI. Y si el crash de `MultipleResultsFound` deja al
sistema resolviendo el actor equivocado en alguna ventana, eso explicaría
el incidente de autorización — cerrar esta causa raíz es el paso más
importante antes de poder confiar en cualquier chequeo de rol del
sistema.

## Solution
Dos cambios en `src/services/miembro_service.py`: (1) `agregar_miembro`
rechaza explícitamente agregar un Usuario que ya tiene una fila `Miembro`
activa en esa casa, antes de poder crear la duplicada; (2)
`resolver_actor_en_casa` deja de asumir `.one_or_none()` — si ya existen
duplicados (datos previos a este fix), resuelve de forma determinística
en vez de crashear. Ver **[Solution Overview](feat/00-overview.md)**.

## Outcome
Ningún request autenticado a una casa puede terminar en 500 por
membresía duplicada, ni antes (nueva duplicación bloqueada) ni después
(duplicados preexistentes tolerados sin crash). El chequeo de rol
Administrador sigue siendo correcto incluso bajo la fila resuelta de
forma determinística.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Cuando un Administrador intenta agregar como miembro a un Usuario que ya tiene una fila `Miembro` activa en esa misma casa, el sistema rechaza la operación con un error claro en vez de crear una segunda fila. | La unicidad exigida es `(casa_id, usuario_id)` entre filas activas — no solo `identificacion`, que ya se validaba. |
| REQ-002 | Cuando `resolver_actor_en_casa` encuentra más de una fila `Miembro` activa para `(casa_id, usuario_id)` — dato preexistente a REQ-001 — resuelve una de forma determinística en vez de propagar una excepción no manejada. | `Miembro` no tiene columna de fecha de creación; determinístico significa "siempre la misma fila para el mismo estado de datos" (orden estable por `Miembro.id`), no "la más antigua" — el objetivo es eliminar el 500, no arbitrar cuál membresía es la "correcta" (eso requeriría una decisión de producto fuera de este fix). |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un Usuario ya tiene una fila `Miembro` activa en la casa X **When** un Administrador intenta agregar el email de ese mismo Usuario como nuevo miembro de la casa X **Then** la API responde 400 nombrando la membresía duplicada, no 201 | `[INTEGRATION]` |
| TC-002 (REQ-001) | **Given** un Usuario es miembro activo de la casa X pero no de la casa Y **When** se agrega el email de ese Usuario como miembro de la casa Y **Then** la operación tiene éxito normalmente (caso de control, no debe romperse) | `[INTEGRATION]` |
| TC-003 (REQ-002) | **Given** una casa tiene (sembrado directo en la base, simulando datos previos a este fix) dos filas `Miembro` activas para el mismo `(casa_id, usuario_id)` **When** ese Usuario hace cualquier request autenticado a esa casa **Then** el request resuelve exitosamente sin 500, siempre con la misma fila (orden estable) | `[INTEGRATION]` |
| TC-004 (REQ-002) | **Given** el escenario de duplicados de TC-003, repitiendo el mismo request 5 veces **When** se compara el `actor` resuelto en cada respuesta **Then** las 5 resoluciones devuelven el mismo `Miembro.id` — el chequeo de rol nunca queda a merced de qué fila devuelva la base en cada corrida | `[INTEGRATION]` |

## Sources

| Type | Reference |
|---|---|
| Session | QA manual profunda del entorno local dockerizado tras shippear `dockerize-local-env`/`ui-modernization`/`usuarios-auth` — 2026-09-14. Traceback de `MultipleResultsFound` e incidente de desactivación capturados en los logs del contenedor `backend` y en el estado de Postgres. |
| Spec | usuarios-auth (specs/auth-backend) | .nybo/plans/usuarios-auth/specs/auth-backend/spec.md |
