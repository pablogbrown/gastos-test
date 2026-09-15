# Suscripciones mensuales de gastos

## Intention

### What
Un Administrador puede crear una suscripción (ej. Netflix, gimnasio):
una descripción, un importe y una categoría que se repiten cada mes. Se
genera automáticamente un gasto real por mes mientras la suscripción
esté activa, sin que nadie tenga que cargarlo a mano. Una pantalla
nueva permite ver y cancelar las suscripciones de la casa.

### Why
Muchos gastos compartidos son recurrentes por naturaleza (servicios,
membresías) — cargarlos a mano todos los meses es trabajo repetitivo y
fácil de olvidar, a diferencia de una compra puntual en cuotas (spec
`gastos-en-cuotas`, con fin definido).

## Solution
Nueva entidad `Suscripcion` (casa, descripción, importe, categoría,
quién paga, activa/inactiva, último mes generado). Al crearla, se genera
de inmediato el gasto del mes actual. Sin ningún scheduler nuevo: cada
vez que se listan los gastos de una casa (pantalla Gastos o Inicio), el
sistema revisa las suscripciones activas y genera el gasto del mes
actual si todavía no existe — el "disparador" es la primera visita del
mes a esa casa, sin importar quién. Depende de **`balance-mensual`**
por la misma razón que `gastos-en-cuotas`. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Un Administrador carga una suscripción una sola vez; a partir de ahí,
cada mes aparece su gasto correspondiente sin que nadie tenga que
recordarlo, hasta que alguien la cancela desde la pantalla nueva.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un Administrador puede crear una suscripción (descripción, importe, categoría); al crearla, se genera de inmediato el gasto del mes actual. | El gasto generado se reparte entre los miembros activos igual que un gasto normal (misma lógica de `registrar_gasto`, sin selección de participantes al crear la suscripción). |
| REQ-002 | Mientras una suscripción esté activa, listar los gastos de la casa genera el gasto del mes actual si todavía no existe para ese mes — sin acción manual de nadie. | Genera como máximo un gasto por suscripción por mes; nunca duplica el del mes ya generado, y nunca reconstruye retroactivamente meses en los que nadie visitó la casa. |
| REQ-003 | Cancelar una suscripción detiene la generación de gastos futuros. | Los gastos ya generados antes de cancelar no se modifican ni se eliminan — cancelar es hacia adelante, nunca retroactivo. |
| REQ-004 | Solo un Administrador puede crear o cancelar una suscripción. | Mismo criterio ya usado para agregar/desactivar un miembro. |
| REQ-005 | Existe una pantalla "Suscripciones" que lista las de la casa (activas e inactivas) y ofrece cancelar las activas. | La acción "Cancelar" solo se ofrece para una suscripción activa, y solo a un Administrador. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** una casa sin suscripciones **When** un Administrador crea una suscripción de $5.000 **Then** la API responde 201 y ya existe un gasto de $5.000 del mes actual vinculado a esa suscripción | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** una suscripción activa cuyo último mes generado es el mes pasado **When** se listan los gastos de la casa **Then** se genera automáticamente el gasto del mes actual | `[INTEGRATION]` |
| TC-003 (REQ-002, control) | **Given** una suscripción activa cuyo último mes generado ya es el actual **When** se listan los gastos de la casa dos veces seguidas **Then** no se genera un segundo gasto para ese mes | `[INTEGRATION]` |
| TC-004 (REQ-003) | **Given** una suscripción activa con un gasto ya generado este mes **When** se cancela y luego se listan los gastos en un mes futuro **Then** no se genera ningún gasto nuevo para esa suscripción, y el gasto ya generado sigue existiendo sin cambios | `[INTEGRATION]` |
| TC-005 (REQ-004) | **Given** un usuario con rol `member` **When** intenta crear o cancelar una suscripción **Then** la API responde 403 | `[INTEGRATION]` |
| TC-006 (REQ-005) | **Given** una casa con una suscripción activa y otra cancelada **When** se renderiza la pantalla Suscripciones **Then** ambas aparecen listadas, y "Cancelar" se muestra solo para la activa | `[UNIT]` |
| TC-007 (REQ-001) | **Given** el formulario "Nuevo gasto" con el modo "Suscripción mensual" elegido **When** se envía **Then** se llama a `crearSuscripcion`, no a `registrarGasto` | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió, junto con cuotas, que un gasto mensual se trate como suscripción con una pantalla de cancelación — 2026-09-15. Confirmado vía preguntas de aclaración: auto-generar cada mes hasta cancelar, disparado al listar gastos (sin scheduler nuevo). |
| Spec | balance-mensual | .nybo/plans/balance-mensual/spec.md |
| Spec | gastos-en-cuotas | .nybo/plans/gastos-en-cuotas/spec.md |
