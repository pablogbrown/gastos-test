# Estado de pago de un gasto

## Intention

### What
Cada gasto registra si ya está saldado ("Pagado") o todavía no
("A pagar"). Un gasto cargado a mano nace "Pagado" (se asume que ya se
abonó al cargarlo); un gasto generado automáticamente (cuota futura,
suscripción mensual, consumo importado de un resumen de tarjeta) nace
"A pagar". El estado se puede cambiar con un clic desde el listado.

### Why
Hoy no hay forma de saber, mirando el listado de Gastos, cuáles ya están
saldados (ej. la tarjeta ya se pagó) y cuáles siguen pendientes (una
cuota futura, un consumo recién importado). El Balance ya calcula quién
le debe a quién dentro de la casa, pero eso es una cosa distinta: esto
es "¿está saldada esta compra/resumen en sí?".

## Solution
`Gasto` gana una columna `estado` (`"pagado"` default | `"a_pagar"`).
`registrar_gasto` acepta un parámetro `estado` opcional (default
`"pagado"`); las cuotas de una misma compra heredan el mismo valor que
se pasó al registrarlas (igual que ya pasa con `moneda`). Los
generadores automáticos (suscripción mensual, importación de resumen de
tarjeta) pasan explícitamente `estado="a_pagar"`. El estado es puramente
informativo: **no cambia ningún cálculo de Balance**, que sigue sumando
todos los gastos del mes exactamente igual que hoy. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Después de importar un resumen de tarjeta, sus ~17 gastos aparecen
marcados "A pagar" en el listado; al pagar la tarjeta, un clic sobre
cada uno (o sobre todos) los pasa a "Pagado" — sin que el Balance del
mes cambie un solo peso.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un gasto se registra con `estado="pagado"` por defecto, o `"a_pagar"` si se indica explícitamente. | Aplica a un gasto cargado a mano desde el formulario. |
| REQ-002 | Las cuotas generadas al registrar un gasto en cuotas heredan el mismo `estado` indicado al crearlas. | Todas las cuotas de una misma compra comparten el mismo `estado` inicial (igual que comparten `moneda`). |
| REQ-003 | Un gasto generado automáticamente por una suscripción mensual nace con `estado="a_pagar"`. | Nadie confirmó todavía que ese cargo automático esté saldado. |
| REQ-004 | Un gasto creado al importar un resumen de tarjeta (consumo normal, cuota restante o suscripción detectada) nace con `estado="a_pagar"`. | El resumen recién se importó — el usuario todavía no pagó esa tarjeta. |
| REQ-005 | El estado de un gasto se puede cambiar entre "pagado" y "a_pagar" en cualquier momento. | Cualquier miembro de la casa puede cambiarlo — mismo nivel de permiso que registrar un gasto. |
| REQ-006 | Cambiar el estado de un gasto no modifica ningún cálculo de Balance. | El Balance sigue sumando todos los gastos del mes, sin filtrar por estado. |
| REQ-007 | Un valor de `estado` distinto de `"pagado"`/`"a_pagar"` es rechazado. | Aplica tanto al crear como al actualizar. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un gasto sin `estado` **When** se registra **Then** persiste con `estado="pagado"` | `[INTEGRATION]` |
| TC-002 (REQ-001) | **Given** un gasto con `estado="a_pagar"` **When** se registra **Then** persiste así | `[INTEGRATION]` |
| TC-003 (REQ-002) | **Given** un gasto en 3 cuotas con `estado="a_pagar"` **When** se registra **Then** las 3 cuotas tienen `estado="a_pagar"` | `[INTEGRATION]` |
| TC-004 (REQ-003) | **Given** una suscripción activa **When** se genera su gasto mensual **Then** el gasto generado tiene `estado="a_pagar"` | `[INTEGRATION]` |
| TC-005 (REQ-004) | **Given** la importación de un resumen de tarjeta **When** se crean sus gastos **Then** todos (normales, cuotas restantes, suscripción detectada) tienen `estado="a_pagar"` | `[INTEGRATION]` |
| TC-006 (REQ-005) | **Given** un gasto en `"a_pagar"` **When** se actualiza su estado a `"pagado"` **Then** el cambio persiste, y viceversa | `[INTEGRATION]` |
| TC-007 (REQ-007) | **Given** una actualización con `estado="otro"` **When** se envía **Then** la API responde 400 | `[INTEGRATION]` |
| TC-008 (REQ-006, control) | **Given** un gasto del mes actual **When** se cambia su estado y se recalcula el Balance **Then** los montos de Balance no cambian | `[INTEGRATION]` |
| TC-009 (REQ-001) | **Given** el formulario "Nuevo gasto" con Estado en "A pagar" **When** se envía **Then** el body incluye `estado: "a_pagar"` | `[UNIT]` |
| TC-010 (REQ-005) | **Given** un gasto "A pagar" en el listado **When** se hace clic en su chip de estado **Then** se llama a la API de actualización y el chip pasa a "Pagado" | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió que los gastos registren su estado de pago (pagado/a pagar) — 2026-09-16. Confirmado vía preguntas de aclaración: estado propio del gasto (no por participante), puramente informativo (no afecta Balance). |
