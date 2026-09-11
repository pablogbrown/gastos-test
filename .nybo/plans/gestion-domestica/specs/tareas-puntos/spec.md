# Gestión de Tareas y Puntos

## Intention

### What
Permite a los miembros de una casa crear tareas domésticas, asignarlas o dejarlas disponibles para cualquiera, completarlas, y acumular puntos que se reflejan en un ranking y en un historial.

### Why
Repartir el trabajo doméstico de forma justa requiere visibilidad de qué hay pendiente y un incentivo que reconozca la participación de cada persona.

## Solution
Un modelo Tarea con estado (Pendiente/En curso/Completada), puntos y responsable opcional. Al completarse, se genera un registro inmutable en HistorialTarea con quién, cuándo y cuántos puntos obtuvo; el ranking se deriva agregando ese historial por miembro. Las tareas recurrentes generan una nueva instancia al completarse.
See **[Solution Overview](feat/00-overview.md)** for the full architecture, data model, contracts, and UX/UI.

## Outcome
Cualquier miembro puede ver qué tareas hay pendientes, tomarlas o completar las que le fueron asignadas, y la casa entera puede ver quién está participando más gracias al ranking de puntos — sin perder el registro histórico aunque alguien se dé de baja.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un miembro debe poder crear una tarea doméstica indicando nombre y cantidad de puntos, y opcionalmente descripción, responsable y fecha prevista. | El nombre y la cantidad de puntos son obligatorios; descripción, responsable y fecha prevista son opcionales. |
| REQ-002 | Toda tarea debe encontrarse en uno de los siguientes estados: Pendiente, En curso, Completada. | Una tarea se crea en estado Pendiente por defecto. |
| REQ-003 | Una tarea puede estar asignada a un miembro específico o disponible para cualquier miembro de la casa. | Si está disponible para cualquiera, cualquier miembro activo puede tomarla y completarla. |
| REQ-004 | Cuando una tarea se marca como completada, el sistema debe registrar quién la realizó, cuándo, y otorgar los puntos correspondientes. | Los puntos solo se otorgan al completar la tarea, y nunca más de una vez por cada realización de esa tarea. |
| REQ-005 | El sistema debe acumular los puntos obtenidos por cada miembro dentro de la casa. | Los puntos acumulados deben quedar disponibles en el historial y no eliminarse al completarse nuevas tareas. |
| REQ-006 | La casa debe contar con un ranking de miembros ordenado por puntos totales, de mayor a menor. | El ranking se recalcula cada vez que un miembro obtiene puntos nuevos. |
| REQ-007 | El sistema debe permitir definir tareas recurrentes que vuelvan a estar disponibles automáticamente después de completarse. | Al completarse una tarea recurrente, se genera una nueva instancia en estado Pendiente según su frecuencia definida. |
| REQ-008 | El sistema debe mantener un historial de tareas realizadas, indicando tarea, persona, fecha y puntos obtenidos. | El historial debe conservar registros de miembros que luego fueron desactivados. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un miembro activo **When** crea la tarea "Lavar los platos" con 5 puntos **Then** la tarea se guarda con esos datos | `[UNIT]` |
| TC-002 (REQ-001) | **Given** un miembro activo **When** intenta crear una tarea sin nombre **Then** el sistema rechaza la operación | `[UNIT]` |
| TC-003 (REQ-002) | **Given** una tarea recién creada **When** se consulta su estado **Then** figura como Pendiente | `[UNIT]` |
| TC-004 (REQ-003) | **Given** una tarea sin responsable asignado **When** cualquier miembro activo la marca como completada **Then** la tarea queda asociada a quien la completó y obtiene los puntos | `[UNIT]` |
| TC-005 (REQ-004) | **Given** una tarea de 10 puntos completada por Pablo **When** se registra la finalización **Then** se guarda quién, cuándo, y se otorgan 10 puntos a Pablo | `[UNIT]` |
| TC-006 (REQ-004) | **Given** una tarea ya completada **When** se intenta marcarla como completada nuevamente sin una nueva instancia **Then** el sistema rechaza la operación y no otorga puntos adicionales | `[UNIT]` |
| TC-007 (REQ-005) | **Given** un miembro que completó 3 tareas (5+3+10 puntos) **When** se consulta su total **Then** el sistema muestra 18 puntos acumulados | `[UNIT]` |
| TC-008 (REQ-006) | **Given** los puntos acumulados de 4 miembros **When** se consulta el ranking **Then** aparecen ordenados de mayor a menor puntaje | `[UNIT]` |
| TC-009 (REQ-007) | **Given** una tarea recurrente semanal recién completada **When** se procesa la recurrencia **Then** se genera una nueva instancia en estado Pendiente | `[INTEGRATION]` |
| TC-010 (REQ-008) | **Given** un miembro desactivado que completó tareas antes de desactivarse **When** se consulta el historial **Then** sus registros siguen apareciendo | `[INTEGRATION]` |

## Sources

| Type | Reference | Location |
|---|---|---|
| Doc | Aplicación de Gestión Doméstica — Especificación Funcional | Aplicación de Gestión Doméstica — Especificación Funcional.md (§8-14, §18) |
| Spec | casas-miembros | .nybo/plans/gestion-domestica/specs/casas-miembros/spec.md |
