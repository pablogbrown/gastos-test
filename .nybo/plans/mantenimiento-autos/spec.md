# Mantenimiento de autos

## Intention

### What
Nueva pantalla "Mantenimiento Autos" para registrar los autos de la
casa y cargarles sus services/mantenimientos (ej. "cambio de aceite",
"rotación de neumáticos") — con la misma mecánica ya construida en
`mantenimiento-casa` (fecha estimada, periodicidad, materiales/repuestos,
alerta), asociada a un auto específico.

### Why
El mantenimiento de un auto es conceptualmente igual al de la casa
(algo que hay que hacer en una fecha, a veces recurrente, a veces con
repuestos) pero corresponde a un vehículo puntual, no a la casa en
general — necesita su propia pantalla y agrupar los ítems por auto.

## Solution
Nueva entidad `Auto` (marca, modelo, patente opcional, año opcional),
de la casa (no de un miembro específico). `ItemMantenimiento` (ya
existente) gana un `auto_id` opcional: `NULL` sigue siendo mantenimiento
de la casa (pantalla "Mantenimiento", sin cambios); poblado es
mantenimiento de un auto puntual, visible en la nueva pantalla
"Mantenimiento Autos", agrupado por auto. Reutiliza `mantenimiento_
service` tal cual (crear/completar/materiales/alerta) — sin duplicar
esa lógica. La alerta de Inicio ya construida en `mantenimiento-casa`
incluye automáticamente los ítems de autos próximos a vencer. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Pablo registra su auto (Toyota Corolla, patente AB123CD) y le carga
"Cambio de aceite", fecha estimada en 2 meses, con materiales "Aceite
10W40 (4 litros)" y "Filtro de aceite (1)". El ítem aparece en
"Mantenimiento Autos" agrupado bajo ese auto; si se acerca la fecha,
aparece en el mismo banner de Inicio que ya muestra mantenimiento de la
casa.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Se puede registrar un auto de la casa con marca, modelo, patente opcional y año opcional. | El auto es de la casa, no de un miembro específico — cualquier miembro activo puede registrarlo y verlo. |
| REQ-002 | Un ítem de mantenimiento puede asociarse a un auto específico, con los mismos campos y mecanismo que mantenimiento de la casa (fecha estimada, periodicidad, materiales, alerta). | Reutiliza `mantenimiento_service` sin duplicar su lógica. |
| REQ-003 | "Mantenimiento Autos" vive en su propia pantalla, separada de "Mantenimiento" (de la casa), mostrando los ítems agrupados por auto. | Un ítem con `auto_id=NULL` nunca aparece acá; uno con `auto_id` poblado nunca aparece en "Mantenimiento" de la casa. |
| REQ-004 | La alerta de vencimiento en Inicio incluye también los ítems de mantenimiento de autos próximos a vencer. | Mismo banner ya construido en `mantenimiento-casa`, sin una sección separada. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** datos válidos de auto **When** se registra **Then** persiste y aparece en el listado de la casa | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** un `auto_id` válido **When** se crea un ítem de mantenimiento con ese `auto_id` **Then** queda asociado a ese auto | `[INTEGRATION]` |
| TC-003 (REQ-003) | **Given** ítems con y sin `auto_id` **When** se listan por casa sin filtro **Then** solo devuelve los de `auto_id=NULL`; **When** se listan filtrando por un auto **Then** solo devuelve los de ese auto | `[INTEGRATION]` |
| TC-004 (REQ-004) | **Given** un ítem de auto próximo a vencer **When** se arma el dashboard **Then** aparece en `mantenimientoConAlerta`, igual que uno de la casa | `[INTEGRATION]` |
| TC-005 (REQ-001, control) | **Given** un auto de una casa **When** se intenta usar su id desde otra casa **Then** la API responde 404 | `[INTEGRATION]` |
| TC-006 (REQ-001/002, frontend) | **Given** la pantalla "Mantenimiento Autos" **When** se registra un auto y se le carga un ítem **Then** ambos aparecen agrupados correctamente | `[UNIT]` |
| TC-007 (REQ-003, control de regresión) | **Given** la pantalla "Mantenimiento" (de la casa) **When** se renderiza tras esta spec **Then** sigue funcionando exactamente igual, sin mostrar ítems de autos | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió un menú separado para cargar mantenimiento de los autos de la casa — 2026-09-16. Confirmado vía preguntas de aclaración: autos de la casa (no de un miembro), periodicidad por fecha (sin trackear kilometraje). |
| Spec | mantenimiento-casa | .nybo/plans/mantenimiento-casa/spec.md |
