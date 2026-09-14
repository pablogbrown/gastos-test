# Fix — Ranking y dashboard muestran UUIDs crudos en vez de nombres

## Intention

### What
La pantalla Ranking (`entrada.miembroId`) y la sección "Tareas
completadas recientes" del dashboard (`${registro.miembro_id} completó
una tarea...`) muestran el UUID crudo del Miembro en vez de su nombre.
`App.tsx` ya obtiene la lista de miembros de la casa (se la pasa a
`<Gastos>`), pero no a `<Ranking>` ni a `<InicioCasa>`.

### Why
Un UUID no le dice nada a un usuario real — "b94dc056-3d07-4256..." en
vez de "Administrador" hace que el ranking y la actividad reciente sean
ilegibles en la práctica, justo las dos pantallas pensadas para dar un
vistazo rápido del estado de la casa.

## Solution
Pasar la lista `miembros` (ya cargada en `App.tsx`) como prop a
`<Ranking>` y a `<InicioCasa>`, y resolver el nombre por id en ambas
pantallas — mismo patrón ya usado en `Gastos.tsx`/`Tareas.tsx`
(`miembros.find((m) => m.id === id)?.nombre ?? id`, con el id crudo como
fallback si el miembro no aparece en la lista, ej. fue eliminado). Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Ranking y "Tareas completadas recientes" muestran el nombre del miembro
en vez de su UUID, sin cambiar ningún dato ni endpoint — es puramente
una resolución de presentación en el cliente, igual a como ya funcionan
Gastos y Tareas.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | La pantalla Ranking muestra el nombre del miembro en cada fila en vez de su `miembroId`. | Si el miembro no está en la lista recibida (ej. fue desactivado y excluido en otro punto), se muestra el id crudo como fallback — nunca una fila vacía o rota. |
| REQ-002 | La sección "Tareas completadas recientes" del dashboard muestra el nombre del miembro que completó cada tarea en vez de su `miembro_id`. | Mismo fallback que REQ-001. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un ranking con una entrada cuyo `miembroId` corresponde a un miembro llamado "Ana" en la lista de miembros recibida **When** se renderiza `Ranking` **Then** la fila muestra "Ana", no el UUID | `[UNIT]` |
| TC-002 (REQ-001) | **Given** una entrada de ranking cuyo `miembroId` no está en la lista de miembros recibida **When** se renderiza `Ranking` **Then** la fila muestra el UUID crudo como fallback, sin romper el render | `[UNIT]` |
| TC-003 (REQ-002) | **Given** un dashboard con una tarea completada por "Ana" **When** se renderiza `InicioCasa` **Then** "Tareas completadas recientes" muestra "Ana completó una tarea...", no su UUID | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | QA manual profunda del entorno local dockerizado — 2026-09-14. |
