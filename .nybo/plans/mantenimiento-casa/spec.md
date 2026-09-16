# Mantenimiento de la casa

## Intention

### What
Nueva pantalla "Mantenimiento" para cargar cuestiones de mantenimiento
de la casa (ej. "arreglar el reflector de la entrada", "poner membrana
al techo"): descripción, fecha estimada de realización, periodicidad
(si es recurrente) y una lista de materiales necesarios. Un ítem
próximo a vencer genera una alerta visual en Inicio.

### Why
Hoy no hay ningún lugar para trackear el mantenimiento de la casa —
"Tareas" está pensado para tareas domésticas con puntos/ranking entre
miembros, no para este tipo de trabajos (a veces caros, a veces con
compras previas de materiales).

## Solution
Nueva entidad `ItemMantenimiento` (nombre, descripción, fecha estimada,
recurrente + periodicidad, estado pendiente/completado) con una lista
de materiales estructurada (`MaterialMantenimiento`: nombre, cantidad,
conseguido). Un ítem recurrente exige periodicidad Y fecha estimada
(mismo criterio recién corregido en Tareas) — al completarlo, se genera
una nueva instancia pendiente con la fecha siguiente según su
periodicidad, no completable antes de esa fecha. Un ítem cuyo
vencimiento está a 7 días o menos (o ya venció) aparece en un banner de
alerta en Inicio — mismo patrón que tarjetas de crédito. En la
navegación, "Mantenimiento" se agrupa junto con "Tareas" (que pasa de
suelta a grupo). Ver **[Solution Overview](feat/00-overview.md)**.

## Outcome
Pablo carga "Poner membrana al techo", periodicidad anual, fecha
estimada en 3 meses, con materiales "Membrana asfáltica (2)" y
"Silicona (1)". Puede ir marcando cada material como conseguido. Cuando
falten 7 días para la fecha, aparece un banner en Inicio.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Se puede registrar un ítem de mantenimiento con nombre, descripción opcional y fecha estimada opcional. | Sin fecha estimada, el ítem no puede ser recurrente ni generar alerta. |
| REQ-002 | Un ítem puede ser recurrente con una periodicidad (semanal/mensual/trimestral/semestral/anual). | Recurrente exige periodicidad Y fecha estimada — mismo criterio que ya rige para Tareas. |
| REQ-003 | Un ítem puede tener una lista de materiales necesarios, cada uno con nombre y cantidad, marcable como conseguido/pendiente por separado. | Los materiales se pueden agregar al crear el ítem o después. |
| REQ-004 | Al completar un ítem recurrente, se genera una nueva instancia pendiente con la fecha estimada siguiente según su periodicidad. | No se puede completar esa nueva instancia antes de su propia fecha estimada (409) — mismo criterio recién corregido en Tareas. |
| REQ-005 | Un ítem con fecha estimada a 7 días o menos (o ya vencida) genera una alerta visible en Inicio. | Mismo umbral y criterio ya usado para el vencimiento de tarjetas de crédito. |
| REQ-006 | "Mantenimiento" vive en su propia pantalla, agrupada junto con "Tareas" en el menú superior desktop. | "Tareas" pasa de suelta a grupo (mismo mecanismo ya usado por `nav-agrupada`); la barra inferior mobile no cambia. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** datos válidos **When** se registra un ítem **Then** persiste en estado "pendiente" | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** un ítem recurrente sin periodicidad o sin fecha estimada **When** se registra **Then** la API responde 400 | `[INTEGRATION]` |
| TC-003 (REQ-003) | **Given** un ítem con materiales al crearlo **When** se registra **Then** cada material persiste con nombre, cantidad y `conseguido=false` | `[INTEGRATION]` |
| TC-004 (REQ-003) | **Given** un material de un ítem **When** se marca como conseguido **Then** el cambio persiste | `[INTEGRATION]` |
| TC-005 (REQ-004) | **Given** un ítem no recurrente **When** se completa **Then** queda "completado" sin generar ninguna instancia nueva | `[INTEGRATION]` |
| TC-006 (REQ-004) | **Given** un ítem recurrente con periodicidad "mensual" **When** se completa **Then** se genera una nueva instancia pendiente con fecha estimada = fecha actual + 1 mes | `[INTEGRATION]` |
| TC-007 (REQ-004) | **Given** la nueva instancia generada **When** se intenta completar antes de su fecha estimada **Then** la API responde 409 | `[INTEGRATION]` |
| TC-008 (REQ-005) | **Given** un ítem con fecha estimada a 5 días **When** se arma el dashboard **Then** aparece en la alerta; a 20 días, no aparece | `[UNIT]` |
| TC-009 (REQ-001/003, frontend) | **Given** el formulario "Nuevo ítem" con materiales agregados **When** se envía **Then** el ítem creado aparece en el listado con sus materiales | `[UNIT]` |
| TC-010 (REQ-005/006, frontend) | **Given** Inicio con un ítem de mantenimiento próximo a vencer **When** carga **Then** se renderiza el banner correspondiente | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió un apartado de mantenimiento de la casa (fecha estimada, periodicidad, recordatorios, lista de materiales) — 2026-09-16. Confirmado vía preguntas de aclaración: alerta visual (no notificaciones reales), lista de materiales estructurada con cantidad. |
| Spec | mantenimiento-autos | .nybo/plans/mantenimiento-autos/spec.md |
