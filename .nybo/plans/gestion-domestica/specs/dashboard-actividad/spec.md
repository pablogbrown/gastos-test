# Vista General y Actividad de la Casa

## Intention

### What
Ofrece una pantalla principal por casa con el estado general (miembros, gastos recientes, balance, tareas pendientes/completadas recientes, ranking) y un historial general de actividad con las acciones relevantes ocurridas en la casa.

### Why
Los miembros necesitan responder rápido "¿qué pasó en la casa?" sin recorrer por separado gastos, tareas y ranking; y necesitan trazabilidad de quién hizo qué y cuándo.

## Solution
Un servicio de agregación que consulta los módulos de gastos y tareas ya existentes para armar la vista principal, y un registro de actividad (event log) alimentado por hooks desde esos mismos módulos cada vez que ocurre una acción relevante.
See **[Solution Overview](feat/00-overview.md)** for the full architecture, data model, contracts, and UX/UI.

## Outcome
Al entrar a una casa, cualquier miembro ve de un vistazo su situación económica y de tareas, y puede repasar cronológicamente lo que fue pasando (quién gastó, quién completó qué, quién sumó puntos, quién se unió).

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Cada casa debe tener una pantalla principal que muestre miembros, gastos recientes, balance económico, tareas pendientes, tareas recientemente completadas y ranking de puntos. | "Recientes" se define como los últimos 10 registros por sección, ordenados por fecha descendente (asunción — el documento no fija un número). |
| REQ-002 | El sistema debe registrar en un historial general de actividad las acciones relevantes de la casa (gasto registrado, tarea completada, puntos obtenidos, miembro agregado, tarea creada). | Cada entrada debe incluir tipo de acción, miembro involucrado, fecha y una descripción legible en lenguaje natural. |
| REQ-003 | El historial de actividad debe ser consultable en orden cronológico por cualquier miembro de la casa. | Se muestra del más reciente al más antiguo; no requiere rol Administrador. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** una casa con gastos y tareas registrados **When** un miembro abre la pantalla principal **Then** ve miembros, gastos recientes, balance, tareas pendientes, tareas completadas recientes y ranking | `[E2E]` |
| TC-002 (REQ-001) | **Given** una casa recién creada sin gastos ni tareas **When** se abre la pantalla principal **Then** cada sección se muestra vacía sin error | `[UNIT]` |
| TC-003 (REQ-002) | **Given** un miembro que registra un gasto **When** la operación se completa **Then** se agrega una entrada al historial de actividad describiendo el gasto | `[INTEGRATION]` |
| TC-004 (REQ-002) | **Given** un miembro que completa una tarea **When** la operación se completa **Then** se agregan entradas al historial describiendo la tarea completada y los puntos obtenidos | `[INTEGRATION]` |
| TC-005 (REQ-003) | **Given** varias entradas de actividad con distintas fechas **When** se consulta el historial **Then** se listan de la más reciente a la más antigua | `[UNIT]` |

## Sources

| Type | Reference | Location |
|---|---|---|
| Doc | Aplicación de Gestión Doméstica — Especificación Funcional | Aplicación de Gestión Doméstica — Especificación Funcional.md (§15-16, §19) |
| Spec | gastos | .nybo/plans/gestion-domestica/specs/gastos/spec.md |
| Spec | tareas-puntos | .nybo/plans/gestion-domestica/specs/tareas-puntos/spec.md |
