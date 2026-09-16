# Confirmación mutua de un préstamo

## Intention

### What
Un préstamo recién registrado no queda activo de inmediato: la parte
que lo registró (prestamista o deudor) queda confirmada
automáticamente, y la otra parte debe confirmarlo o rechazarlo
explícitamente. Solo cuando ambas partes lo confirmaron, el préstamo
pasa a su ciclo normal de pagado/pendiente; si cualquiera de las dos lo
rechaza, queda marcado "Rechazado" y nunca cuenta como una deuda real.

### Why
Hoy cualquier miembro puede cargar un préstamo entre otros dos sin que
ninguno de los dos lo confirme — un miembro podría (por error o mala
fe) registrar un préstamo que nunca ocurrió. Exigir la confirmación de
la otra parte evita cargas que no correspondan.

## Solution
`Prestamo` gana dos campos de confirmación por rol
(`confirmado_prestamista`/`confirmado_deudor`, cada uno `NULL`
=pendiente, `true`=confirmado, `false`=rechazado). Al crear el
préstamo, el rol de quien lo registra (si es el prestamista o el
deudor) queda confirmado automáticamente; si quien lo registra no es
ninguno de los dos, ambos quedan pendientes. Un préstamo pendiente de
confirmación es visible para toda la casa. Solo el prestamista o el
deudor de ESE préstamo pueden confirmarlo o rechazarlo — nunca un
tercero. El ciclo pagado/pendiente ya existente (`gastos-estado-pago`-
style) solo se puede tocar una vez que ambas partes confirmaron. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Pablo registra un préstamo a Maca. Pablo queda confirmado
automáticamente (es el prestamista); Maca ve el préstamo como
"Pendiente de confirmación" con botones "Confirmar"/"Rechazar" en su
propia fila. Si confirma, el préstamo pasa a "Pendiente" (de devolver);
si rechaza, queda "Rechazado" para siempre.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Al registrar un préstamo, el rol de quien lo registra (prestamista o deudor) queda confirmado automáticamente. | Aplica solo si quien registra es una de las dos partes del préstamo. |
| REQ-002 | Si quien registra el préstamo no es ni el prestamista ni el deudor, ambas partes quedan pendientes de confirmar. | Mismo nivel de apertura ya existente: cualquier miembro activo puede registrar un préstamo entre otros dos. |
| REQ-003 | Un préstamo pendiente de confirmación es visible para toda la casa, marcado como tal. | Mismo criterio de transparencia que el resto de la app. |
| REQ-004 | Solo el prestamista o el deudor de un préstamo pueden confirmarlo o rechazarlo. | Un tercero que lo intente recibe un error de permiso. |
| REQ-005 | Si cualquiera de las dos partes lo rechaza, el préstamo queda "Rechazado" de forma permanente. | Nunca cuenta como una deuda real ni se puede revertir a confirmado. |
| REQ-006 | El estado de devolución (pagado/pendiente) de un préstamo solo se puede cambiar una vez que ambas partes lo confirmaron. | Intentarlo antes es rechazado. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** el prestamista registra el préstamo **When** se crea **Then** su rol queda confirmado y el del deudor queda pendiente | `[INTEGRATION]` |
| TC-002 (REQ-001) | **Given** el deudor registra el préstamo **When** se crea **Then** su rol queda confirmado y el del prestamista queda pendiente | `[INTEGRATION]` |
| TC-003 (REQ-002) | **Given** un tercer miembro registra el préstamo **When** se crea **Then** ambos roles quedan pendientes | `[INTEGRATION]` |
| TC-004 (REQ-004) | **Given** un miembro que no es parte del préstamo **When** intenta confirmarlo o rechazarlo **Then** la API responde 403 | `[INTEGRATION]` |
| TC-005 (REQ-004/REQ-005) | **Given** la parte pendiente **When** confirma su rol **Then**, con ambos roles confirmados, el préstamo queda "confirmado" | `[INTEGRATION]` |
| TC-006 (REQ-005) | **Given** la parte pendiente **When** rechaza el préstamo **Then** queda "rechazado" de forma permanente | `[INTEGRATION]` |
| TC-007 (REQ-006) | **Given** un préstamo todavía no confirmado por ambas partes **When** se intenta cambiar su estado pagado/pendiente **Then** la API responde 400 | `[INTEGRATION]` |
| TC-008 (REQ-003) | **Given** un préstamo pendiente de confirmación **When** se lista **Then** aparece marcado como tal para cualquier miembro | `[UNIT]` |
| TC-009 (REQ-004) | **Given** el listado de préstamos **When** lo ve la parte a la que le toca confirmar **Then** ve los botones "Confirmar"/"Rechazar" en esa fila; cualquier otro miembro solo ve la marca de "Pendiente de confirmación" | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió que un préstamo quede pendiente hasta que ambas partes lo confirmen, para evitar cargas que no correspondan — 2026-09-16, adjuntando una captura de la pantalla Préstamos. Confirmado vía preguntas de aclaración: solo la otra parte confirma (el registrante queda confirmado automáticamente); existe rechazo explícito; visible para toda la casa mientras espera confirmación. |
| Spec | prestamos-entre-miembros | .nybo/plans/prestamos-entre-miembros/spec.md |
