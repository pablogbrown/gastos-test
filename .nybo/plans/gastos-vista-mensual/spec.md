# Vista mensual del listado de Gastos

## Intention

### What
La pantalla Gastos gana un selector de mes (igual al que ya tiene
Balance) que filtra el listado para mostrar solo los gastos de ese mes
— en vez de una única lista con todo el historial mezclado.

### Why
Hoy Gastos muestra todos los gastos desde siempre en una sola lista
larga (ver captura adjunta) — con importación de resúmenes y
suscripciones generando varios gastos por mes, se vuelve difícil
encontrar algo sin scrollear todo el historial.

## Solution
`listar_gastos` acepta un parámetro `mes` opcional (`YYYY-MM`); sin él,
devuelve todos los gastos exactamente igual que hoy (compatibilidad con
el dashboard de Inicio, que sigue mostrando los últimos 10 gastos de
toda la casa, no solo del mes). `Gastos.tsx` agrega un selector de mes
(mismo componente y mismo criterio que `Balance.tsx`: mes calendario
actual preseleccionado) y pasa ese valor al pedir el listado. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Al entrar a Gastos, se ve solo lo cargado este mes; cambiar el selector
a un mes anterior muestra el historial de ese mes, sin mezclar fechas.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | `listar_gastos` puede filtrar por mes (`YYYY-MM`), devolviendo solo los gastos cuya fecha cae en ese mes. | Sin `mes`, el comportamiento es idéntico al actual (todos los gastos). |
| REQ-002 | La pantalla Gastos muestra un selector de mes, con el mes calendario actual preseleccionado al entrar. | Mismo componente/criterio que el selector ya existente en Balance. |
| REQ-003 | Cambiar el mes en el selector actualiza el listado para mostrar solo los gastos de ese mes. | No afecta el formulario de alta ni ninguna otra sección de la pantalla. |
| REQ-004 | El dashboard de Inicio ("gastos recientes") no cambia — sigue mostrando los últimos 10 gastos de toda la casa. | `armar_dashboard` sigue llamando a `listar_gastos(casa_id)` sin `mes`. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** gastos en varios meses **When** se listan con `mes="2026-09"` **Then** solo devuelve los de septiembre 2026 | `[INTEGRATION]` |
| TC-002 (REQ-001, control) | **Given** los mismos gastos **When** se listan sin `mes` **Then** devuelve todos, igual que hoy | `[INTEGRATION]` |
| TC-003 (REQ-001) | **Given** un `GET .../gastos?mes=2026-09` **When** se solicita **Then** la respuesta HTTP solo incluye los gastos de ese mes | `[INTEGRATION]` |
| TC-004 (REQ-002/REQ-003) | **Given** la pantalla Gastos con el selector en "2026-09" **When** carga **Then** pide `listarGastos(casaId, "2026-09")` y solo renderiza esos gastos | `[UNIT]` |
| TC-005 (REQ-002) | **Given** la pantalla Gastos recién abierta **When** se inspecciona el selector **Then** el valor preseleccionado es el mes calendario actual | `[UNIT]` |
| TC-006 (REQ-004, control) | **Given** el dashboard de Inicio **When** se arma **Then** sigue mostrando los últimos 10 gastos de toda la casa, sin filtrar por mes | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió ver los gastos mes a mes de forma más amigable (junto con el estado de pago) — 2026-09-16, adjuntando una captura del listado actual sin agrupar. Confirmado vía preguntas de aclaración: selector de mes que filtra la lista, mismo patrón que Balance. |
