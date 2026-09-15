# Gestión de tarjetas de crédito y alerta de vencimiento

## Intention

### What
Un miembro puede registrar sus tarjetas de crédito (banco, nombre,
últimos 4 dígitos) y mantener actualizados el cierre y vencimiento del
resumen vigente. Cuando el vencimiento de alguna tarjeta de la casa está
cerca (o ya pasó), se muestra un banner de alerta al abrir la app.

### Why
Hoy no hay ningún lugar para trackear "cuándo vence tal tarjeta" ni
recordatorio alguno — el usuario lo tiene que recordar de memoria. Es
además la base necesaria para la importación automática de resúmenes
(próxima feature): cada resumen importado pertenece a una tarjeta ya
registrada.

## Solution
Nueva entidad `TarjetaCredito` (banco, nombre, últimos dígitos, fecha de
cierre y vencimiento actuales, saldo actual en ARS y USD, dueño y casa),
con una pantalla "Tarjetas" para crear/editar/eliminar. La app no tiene
notificaciones push/email — la alerta es puramente visual: al armar el
dashboard de Inicio, se calculan las tarjetas cuyo vencimiento está a 7
días o menos (o ya vencido) y se listan en un banner. No hay estado de
"ya visto" — se recalcula en cada carga de Inicio. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Pablo registra su Visa Platinum con vencimiento 07-Sep. El 1° de
septiembre, al abrir la app, ve un banner: "Visa Platinum (BBVA) vence
el 07-Sep — quedan 6 días." Si no la actualiza y pasa la fecha, el
banner sigue mostrándose indicando que ya venció.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un miembro puede registrar una tarjeta con banco, nombre, últimos 4 dígitos, fecha de cierre y vencimiento actuales. | Todos los campos son obligatorios salvo el saldo (aún no se tiene resumen). |
| REQ-002 | Puede editar cierre/vencimiento/saldo de una tarjeta ya registrada. | Pensado para reflejar manualmente el resumen más reciente; no valida que la nueva fecha sea posterior a la anterior. |
| REQ-003 | Puede eliminar (desactivar) una tarjeta. | Desactivar preserva el registro para no perder historial, mismo criterio que desactivar un Miembro. |
| REQ-004 | Al abrir Inicio, si alguna tarjeta activa de la casa vence dentro de los próximos 7 días o ya venció, se muestra un banner con su nombre y fecha. | El umbral de 7 días es una constante del servicio, no configurable en esta spec. |
| REQ-005 | Una tarjeta cuyo vencimiento está a más de 7 días no genera ningún banner. | Evita ruido — el banner solo aparece cuando es accionable. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** datos válidos de tarjeta **When** se registra **Then** persiste y aparece en el listado | `[INTEGRATION]` |
| TC-002 (REQ-001) | **Given** una tarjeta sin banco **When** se registra **Then** la API responde 400 | `[INTEGRATION]` |
| TC-003 (REQ-002) | **Given** una tarjeta existente **When** se edita su vencimiento **Then** el nuevo valor queda persistido | `[INTEGRATION]` |
| TC-004 (REQ-003) | **Given** una tarjeta existente **When** se elimina **Then** ya no aparece en el listado activo | `[INTEGRATION]` |
| TC-005 (REQ-004) | **Given** una tarjeta que vence en 3 días **When** se arma el dashboard **Then** aparece en las tarjetas con alerta | `[UNIT]` |
| TC-006 (REQ-004) | **Given** una tarjeta cuyo vencimiento ya pasó **When** se arma el dashboard **Then** aparece igual, marcada como vencida | `[UNIT]` |
| TC-007 (REQ-005) | **Given** una tarjeta que vence en 20 días **When** se arma el dashboard **Then** no aparece en las tarjetas con alerta | `[UNIT]` |
| TC-008 (REQ-004) | **Given** Inicio con una tarjeta próxima a vencer **When** carga la pantalla **Then** se renderiza el banner con su nombre y fecha | `[UNIT]` |
| TC-009 (REQ-001) | **Given** la pantalla "Tarjetas" **When** se completa y envía el formulario de alta **Then** la tarjeta creada aparece en el listado | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió poder registrar tarjetas de crédito y saber cuándo vence el resumen — 2026-09-15. Confirmado vía preguntas de aclaración: alerta visual dentro de la app (no hay infraestructura de notificaciones). |
