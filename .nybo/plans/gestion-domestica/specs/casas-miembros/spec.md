# Casas y Miembros

## Intention

### What
Permite a un usuario crear una Casa, agregar y administrar sus Miembros, y aplicar los roles Administrador/Miembro que gobiernan qué puede hacer cada persona dentro de esa casa.

### Why
Es la base sobre la que se apoyan la gestión de gastos y de tareas domésticas: nadie puede registrar un gasto o completar una tarea sin pertenecer antes a una casa con un rol definido.

## Solution
Un modelo Casa con una colección de Miembros, cada uno con nombre, identificación dentro de la casa y rol (Administrador/Miembro). Quien crea la casa queda automáticamente como su primer miembro y administrador. Los miembros se pueden desactivar sin borrar su actividad histórica.
See **[Solution Overview](feat/00-overview.md)** for the full architecture, data model, contracts, and UX/UI.

## Outcome
Un usuario puede crear una casa nueva, agregar a las personas con quienes convive, y esa casa queda lista para que la gestión de gastos y de tareas (specs dependientes) opere sobre miembros reales con permisos claros. Dar de baja a alguien no borra lo que hizo antes.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un usuario debe poder crear una nueva casa indicando al menos un nombre. | Quien crea la casa queda automáticamente como su primer miembro con rol Administrador. |
| REQ-002 | El administrador de una casa debe poder agregar nuevos miembros indicando nombre e identificación dentro de la casa. | La identificación debe ser única dentro de la misma casa; dos casas distintas pueden reutilizar la misma identificación. |
| REQ-003 | El administrador debe poder eliminar o desactivar un miembro que ya no pertenezca a la casa. | Desactivar/eliminar un miembro no debe borrar el historial de gastos o tareas que haya generado. |
| REQ-004 | El sistema debe reconocer los roles Administrador y Miembro, cada uno con un conjunto de permisos distinto. | Administrador: modificar la casa, agregar/eliminar miembros, crear/modificar tareas, gestionar categorías, consultar todos los gastos y el ranking. Miembro: consultar la casa, registrar gastos, consultar balances, realizar y completar tareas, consultar sus puntos y el ranking. |
| REQ-005 | Toda persona debe pertenecer a una casa para poder registrar gastos o tareas en ella. | Ninguna operación de gasto o tarea puede ejecutarse para un usuario que no figure como miembro activo de esa casa. |
| REQ-006 | Una persona puede participar en más de una casa, y cada casa debe mantener su información independiente de las demás. | Los datos (miembros, gastos, tareas, puntos) de una casa nunca deben mezclarse ni afectar a otra casa. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un usuario autenticado sin casas **When** crea una casa con nombre "Casa Brown" **Then** la casa se crea y el usuario queda como miembro con rol Administrador | `[UNIT]` |
| TC-002 (REQ-001) | **Given** un usuario **When** intenta crear una casa sin nombre **Then** el sistema rechaza la operación con un error de validación | `[UNIT]` |
| TC-003 (REQ-002) | **Given** una casa existente con un administrador **When** el administrador agrega un miembro con nombre e identificación válidos **Then** el miembro queda registrado y activo en esa casa | `[UNIT]` |
| TC-004 (REQ-002) | **Given** una casa con un miembro cuya identificación es "P1" **When** el administrador intenta agregar otro miembro con la misma identificación "P1" **Then** el sistema rechaza la operación por identificación duplicada | `[UNIT]` |
| TC-005 (REQ-003) | **Given** un miembro activo con gastos y tareas registrados **When** el administrador lo desactiva **Then** el miembro queda inactivo y su historial de gastos y tareas permanece intacto | `[INTEGRATION]` |
| TC-006 (REQ-004) | **Given** un usuario con rol Miembro **When** intenta agregar otro miembro a la casa **Then** el sistema rechaza la operación por falta de permisos | `[UNIT]` |
| TC-007 (REQ-004) | **Given** un usuario con rol Administrador **When** consulta el listado completo de gastos de la casa **Then** el sistema los devuelve sin restricción | `[UNIT]` |
| TC-008 (REQ-005) | **Given** un usuario que no es miembro de ninguna casa **When** intenta registrar un gasto **Then** el sistema rechaza la operación | `[INTEGRATION]` |
| TC-009 (REQ-006) | **Given** dos casas distintas cada una con un miembro de igual identificación **When** se consultan ambas casas **Then** cada una muestra únicamente sus propios miembros, gastos y tareas | `[INTEGRATION]` |

## Sources

| Type | Reference | Location |
|---|---|---|
| Doc | Aplicación de Gestión Doméstica — Especificación Funcional | Aplicación de Gestión Doméstica — Especificación Funcional.md (§2-4, §17-18) |
