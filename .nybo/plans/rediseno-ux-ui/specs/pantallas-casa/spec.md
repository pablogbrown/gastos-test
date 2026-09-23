# Pantallas de casa - Technical Specification

| | |
| --- | --- |
| Progress | [progress.md](progress.md) |

## Intention

### What
Aplica el sistema visual de `sistema-visual` a las 4 pantallas sociales/de casa: Miembros, Ranking, Tareas y Actividad — con énfasis en dar peso visual a la gamificación (niveles, rachas, logros) ya existente, hoy mostrada como texto plano.

### Why
Estas 4 pantallas concentran la parte "social" de taskia (quién vive en la casa, quién hizo qué) y son las que más se benefician de un tratamiento visual de perfil/progreso — hoy el nivel, la racha y los logros de `gamificacion-puntos` se muestran como texto sin ninguna jerarquía visual, perdiendo el efecto motivacional que la feature buscaba.

## Outcome
Miembros muestra cada persona como una tarjeta de perfil (avatar/inicial, nombre, rol). Ranking destaca visualmente nivel/racha/logros de cada miembro (no solo texto). Tareas distingue con claridad visual pendiente/completada/asignada a mí. Actividad se lee como un feed cronológico con un ícono por tipo de evento, no una tabla plana.

## Requirements

### REQ-001: Miembros como tarjetas de perfil
Cada miembro de la casa se muestra como una tarjeta de perfil (`Avatar` con inicial del nombre, nombre, rol como chip) en vez de una fila de tabla o lista plana. Un miembro "Pendiente" (invitado sin cuenta aún) se distingue visualmente (chip de estado distinto).

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-001 | **Given** una casa con un Administrador y un Miembro **When** se renderiza Miembros **Then** cada uno aparece como tarjeta con avatar, nombre y chip de rol distintos entre sí. | `[UNIT]` |
| TC-002 | **Given** un miembro con estado "Pendiente" **When** se renderiza su tarjeta **Then** su chip de estado es visualmente distinto (color/label) al de un miembro activo. | `[UNIT]` |

### REQ-002: Ranking con progreso visual
El nivel, la racha y los logros de cada miembro (spec `gamificacion-puntos`) se muestran con jerarquía visual — una barra o indicador de progreso hacia el próximo nivel, un ícono de racha con el número de días, y los logros como chips/badges — en vez de texto plano concatenado.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-003 | **Given** un miembro con 60 puntos (nivel "Activo", a mitad de camino a "Comprometido") **When** se renderiza su fila en Ranking **Then** se muestra un indicador de progreso visual (no solo el número de puntos como texto). | `[UNIT]` |
| TC-004 | **Given** un miembro con 2 logros desbloqueados **When** se renderiza Ranking **Then** ambos logros se muestran como chips/badges distintos entre sí, no como una lista de texto separada por comas. | `[UNIT]` |

### REQ-003: Tareas con estado visual claro
Cada tarea distingue con claridad visual (color/ícono, no solo texto) entre pendiente, completada, y "asignada a mí" — reutilizando los colores semánticos del tema (success para completada).

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-005 | **Given** una tarea completada y otra pendiente **When** se renderiza Tareas **Then** ambas son visualmente distinguibles (color/ícono) sin necesidad de leer el texto de estado. | `[UNIT]` |

### REQ-004: Actividad como feed cronológico
El historial de actividad se muestra como un feed vertical con un ícono distinto por tipo de evento (alta de miembro, gasto registrado, tarea completada, etc.) en vez de una tabla de filas homogéneas.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-006 | **Given** un historial con un evento de "miembro agregado" y otro de "tarea completada" **When** se renderiza Actividad **Then** cada uno usa un ícono distinto asociado a su tipo de evento. | `[UNIT]` |

### REQ-005: Cero regresión funcional
Ningún dato, cliente de API, ni lógica de cálculo (ranking, racha, nivel, logros, actividad) cambia — el restyle es puramente de presentación en las 4 pantallas.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-007 | **Given** el test suite existente de las 4 pantallas (`Miembros.test.tsx`, `Ranking.test.tsx`, `Tareas.test.tsx`, `HistorialActividad.test.tsx`) **When** se corre tras el restyle **Then** los 4 suites pasan sin modificar sus queries por rol/label. | `[INTEGRATION]` |

## Constraints
- REQ-001/002/003/004: reutilizan exclusivamente `PageHeader`/`EmptyState`/tema de `sistema-visual` — ningún ícono/color de tipo de evento se hardcodea fuera de un mapa centralizado por pantalla (mismo patrón `NOMBRES_LOGRO`/`FRONP-03` ya establecido para el catálogo de logros).
- REQ-005: ningún archivo bajo `src/services/`, `src/api/`, o `src/db/` se modifica — exclusivamente frontend de presentación.

## Solution
Se aplican los componentes de `sistema-visual` a las 4 pantallas, una por task, dado que cada una tiene un patrón visual propio y distinto (perfil, progreso/gamificación, lista de tareas, feed) que no comparte receta mecánica con las otras — a diferencia de las pantallas financieras, agruparlas no ahorra trabajo real.

### Task Execution

| Task | File | Description | Dependencies |
| --- | --- | --- | --- |
| T1 | [01-plan-01-miembros.md](feat/01-plan-01-miembros.md) | Miembros como tarjetas de perfil | — |
| T2 | [01-plan-02-ranking.md](feat/01-plan-02-ranking.md) | Ranking con progreso visual | — |
| T3 | [01-plan-03-tareas.md](feat/01-plan-03-tareas.md) | Tareas con estado visual claro | — |
| T4 | [01-plan-04-actividad.md](feat/01-plan-04-actividad.md) | Actividad como feed cronológico | — |

### Verification

| Task | Test cases | Additional gate criteria |
| --- | --- | --- |
| T1 | TC-001, TC-002, TC-007 | `[AUTO]` `Miembros.test.tsx` en verde. |
| T2 | TC-003, TC-004, TC-007 | `[AUTO]` `Ranking.test.tsx` en verde. |
| T3 | TC-005, TC-007 | `[AUTO]` `Tareas.test.tsx` en verde. |
| T4 | TC-006, TC-007 | `[AUTO]` `HistorialActividad.test.tsx` en verde. |

#### Outcome Smoke Test
1. Levantar el stack, navegar a Miembros/Ranking/Tareas/Actividad.
2. Confirmar visualmente: tarjetas de perfil, progreso de nivel/racha/logros destacado, estado de tarea distinguible sin leer texto, feed de actividad con íconos por tipo.
3. Confirmar cero regresión de datos.
4. Gate final: los 4 test suites existentes en verde, `npm run build` sin errores.

## Sources

| Type | Reference | Detail |
| --- | --- | --- |
| Spec | sistema-visual | .nybo/plans/rediseno-ux-ui/specs/sistema-visual/spec.md — provee el tema y los componentes compartidos. |
| Spec | gamificacion-puntos | .nybo/plans/gamificacion-puntos/spec.md — define nivel/racha/logros/meta que Ranking visualiza. |
| Spec | rediseno-ux-ui | .nybo/plans/rediseno-ux-ui/plan.md — feature-level, split rationale. |

## History

| # | Date | Event | Verdict | Summary |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | Spec created — 4 tasks, 7 test cases. |
| 2 | 2026-09-23 | build | ready | T1–T4 implementados, 168/168 tests verdes, 0 regresión funcional. Coverage diferido (new-dependency, D001). "Meta de la casa" en Ranking omitida (J002). |
