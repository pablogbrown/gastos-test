# Fix — Altas y bajas de miembro no quedan en el Historial de actividad

## Intention

### What
Ni agregar ni desactivar un miembro genera una entrada en el Historial
de actividad de la casa. `TipoActividadEnum` ya define
`MIEMBRO_AGREGADO`, pero `registrar_actividad` nunca se invoca desde
`agregar_miembro` — es un valor de enum muerto. No existe ningún tipo
para "miembro desactivado".

### Why
El Historial de actividad es la única vista de auditoría que tiene la
app. Sin estas dos entradas, un cambio en quién pertenece a la casa (o
quién dejó de tener acceso) no deja ningún rastro visible para el resto
de los miembros — justo el tipo de evento que más importa poder revisar
después de un incidente de permisos.

## Solution
Agregar `MIEMBRO_DESACTIVADO` a `TipoActividadEnum` y llamar a
`registrar_actividad` desde `agregar_miembro` (usando el
`MIEMBRO_AGREGADO` ya existente) y desde `desactivar_miembro` (usando el
nuevo `MIEMBRO_DESACTIVADO`), ambas veces después del `commit` exitoso —
mismo patrón que ya siguen `gasto_service`/`tarea_service`. Reflejar el
nuevo tipo en el frontend (`HistorialActividad.tsx`). Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Toda alta o baja de un miembro aparece en "Actividad" de la casa, con el
mismo formato y orden cronológico que el resto de los eventos, sin
requerir ningún cambio en cómo se consulta el historial.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Cuando un Administrador agrega un miembro exitosamente, el sistema registra una entrada `miembro_agregado` en el Historial de actividad de esa casa. | Se registra después del `commit` de `agregar_miembro`, nunca si la operación falló. |
| REQ-002 | Cuando un Administrador desactiva un miembro exitosamente, el sistema registra una entrada `miembro_desactivado` en el Historial de actividad de esa casa. | Se registra después del `commit` de `desactivar_miembro`, nunca si la operación falló. |
| REQ-003 | El frontend reconoce el nuevo tipo `miembro_desactivado` con su propio ícono y etiqueta, igual que los tipos existentes. | Sin este requisito, un tipo de actividad nuevo no reconocido por `ETIQUETAS_TIPO`/`ICONOS_TIPO` rompería el render de esa fila (acceso a índice inexistente). |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** una casa sin actividad previa **When** un Administrador agrega un miembro por email **Then** `GET /casas/{id}/actividad` incluye una entrada `tipo: "miembro_agregado"` con el `miembro_id` del nuevo miembro | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** una casa con un miembro activo **When** un Administrador lo desactiva **Then** `GET /casas/{id}/actividad` incluye una entrada `tipo: "miembro_desactivado"` con el `miembro_id` del miembro desactivado | `[INTEGRATION]` |
| TC-003 (REQ-001, REQ-002) | **Given** un intento de agregar o desactivar que falla (ej. email no registrado, o actor sin rol Administrador) **When** la operación es rechazada **Then** el Historial de actividad no gana ninguna entrada nueva | `[INTEGRATION]` |
| TC-004 (REQ-003) | **Given** el historial de una casa incluye una entrada `miembro_desactivado` **When** se renderiza la pantalla "Actividad" **Then** se muestra con su propio ícono y la etiqueta "Miembro desactivado", sin errores de consola | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | QA manual profunda del entorno local dockerizado — 2026-09-14. Ampliado durante el planning al notar que `MIEMBRO_AGREGADO` ya existe en el enum pero nunca se invoca — el gap real cubre alta y baja, no solo baja. |
