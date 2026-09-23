# Pantallas financieras - Technical Specification

| | |
| --- | --- |
| Progress | [progress.md](progress.md) |

## Intention

### What
Aplica el sistema visual definido en `sistema-visual` (tema + `PageHeader`/`StatCard`/`EmptyState`) a las 7 pantallas de finanzas y mantenimiento de la casa: Gastos, Balance, Tarjetas, Suscripciones, Préstamos, Mantenimiento y Mantenimiento Autos.

### Why
Estas 7 pantallas comparten el mismo patrón visual hoy (lista de ítems + monto/chip de estado + FAB de alta) y son las que un usuario visita con más frecuencia día a día — son las primeras candidatas a beneficiarse del nuevo sistema visual, y su patrón compartido permite aplicar la misma receta de forma consistente en las 7.

## Outcome
Al entrar a cualquiera de las 7 pantallas, el usuario ve un encabezado consistente con acción de alta, tarjetas de línea con esquinas redondeadas y chips de estado con los colores semánticos del nuevo tema (en vez de estilos ad-hoc por pantalla), y un estado vacío ilustrado cuando no hay datos — en vez de una lista o tabla vacía sin ningún mensaje.

## Requirements

### REQ-001: Listas rediseñadas con el sistema visual compartido
Las listas de ítems de las 7 pantallas (gastos, filas de balance, tarjetas, suscripciones, préstamos, ítems de mantenimiento) se reconstruyen como tarjetas de línea (`Card`/`ListItem` bajo el nuevo tema) con chips de estado que usan los colores semánticos definidos en `sistema-visual` (pagado=success, a_pagar=warning, pendiente=warning, rechazado=error) en vez de colores ad-hoc por pantalla.

- Ningún dato ni endpoint cambia — este REQ es puramente de presentación.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-001 | **Given** una lista de gastos con un ítem "Pagado" y otro "A pagar" **When** se renderiza Gastos **Then** cada chip de estado usa el color semántico del tema (success/warning) y no un color hardcodeado por pantalla. | `[UNIT]` |
| TC-002 | **Given** un préstamo con estado "Rechazado" **When** se renderiza Préstamos **Then** su chip usa `palette.error`, igual que cualquier otro estado "Rechazado"/"error" en las otras 6 pantallas. | `[UNIT]` |

### REQ-002: Estados vacíos consistentes
Cuando cualquiera de las 7 pantallas no tiene datos que mostrar (sin gastos este mes, sin tarjetas registradas, sin préstamos, sin ítems de mantenimiento), se muestra el componente `EmptyState` compartido con un mensaje específico al contexto, en vez de una tabla/lista vacía sin mensaje.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-003 | **Given** una casa sin tarjetas registradas **When** se renderiza Tarjetas **Then** se muestra `EmptyState` con mensaje "Todavía no registraste ninguna tarjeta" y una acción para agregar la primera. | `[UNIT]` |
| TC-004 | **Given** un mes sin gastos **When** se renderiza Gastos con el selector de mes en ese mes **Then** se muestra `EmptyState` en vez de una tabla vacía. | `[UNIT]` |

### REQ-003: Encabezado consistente con acción primaria
Las 7 pantallas usan `PageHeader` para su encabezado, con la acción de alta correspondiente (Nuevo gasto, Nueva tarjeta, Nueva suscripción, Nuevo préstamo, Nuevo ítem de mantenimiento) como `action` primaria — reemplazando el botón de alta suelto que cada pantalla posiciona hoy de forma distinta.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-005 | **Given** la pantalla Suscripciones **When** se renderiza **Then** el encabezado es un `PageHeader` cuyo botón de acción abre el mismo formulario de alta que existe hoy. | `[UNIT]` |

### REQ-004: Cero regresión funcional
Ningún cliente de API, cálculo de balance, lógica de reparto de cuotas, ni comportamiento de formularios existente cambia — el restyle es puramente de presentación en las 7 pantallas.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-006 | **Given** el test suite existente de las 7 pantallas (`Gastos.test.tsx`, `Balance.test.tsx`, `Tarjetas.test.tsx`, `Suscripciones.test.tsx`, `Prestamos.test.tsx`, `Mantenimiento.test.tsx`, `MantenimientoAutos.test.tsx`) **When** se corre tras el restyle **Then** los 7 suites pasan sin modificar sus queries por rol/label. | `[INTEGRATION]` |

## Constraints
- REQ-001/002/003: reutilizan exclusivamente los componentes de `sistema-visual` (`PageHeader`, `StatCard`, `EmptyState`, tema) — ninguna pantalla define su propio chip de color o su propio estado vacío ad-hoc.
- REQ-004: ningún archivo bajo `src/services/`, `src/api/`, o `src/db/` se modifica en esta spec — es exclusivamente frontend de presentación.

## Solution
Se aplican los componentes de `sistema-visual` a las 7 pantallas, agrupadas en 4 tasks por afinidad de patrón (movimientos de gasto, tarjetas/suscripciones, préstamos, mantenimiento). Cada task sigue la misma receta: `PageHeader` + tarjetas de línea con chips semánticos + `EmptyState`.

### Task Execution

| Task | File | Description | Dependencies |
| --- | --- | --- | --- |
| T1 | [01-plan-01-gastos-balance.md](feat/01-plan-01-gastos-balance.md) | Gastos + Balance | — |
| T2 | [01-plan-02-tarjetas-suscripciones.md](feat/01-plan-02-tarjetas-suscripciones.md) | Tarjetas + Suscripciones | — |
| T3 | [01-plan-03-prestamos.md](feat/01-plan-03-prestamos.md) | Préstamos | — |
| T4 | [01-plan-04-mantenimiento.md](feat/01-plan-04-mantenimiento.md) | Mantenimiento + Mantenimiento Autos | — |

### Verification

| Task | Test cases | Additional gate criteria |
| --- | --- | --- |
| T1 | TC-001, TC-004, TC-006 | `[AUTO]` `Gastos.test.tsx` y `Balance.test.tsx` en verde. |
| T2 | TC-003, TC-005, TC-006 | `[AUTO]` `Tarjetas.test.tsx` y `Suscripciones.test.tsx` en verde. |
| T3 | TC-002, TC-006 | `[AUTO]` `Prestamos.test.tsx` en verde. |
| T4 | TC-006 | `[AUTO]` `Mantenimiento.test.tsx` y `MantenimientoAutos.test.tsx` en verde. |

#### Outcome Smoke Test
1. Levantar el stack, navegar a cada una de las 7 pantallas.
2. Confirmar visualmente: encabezado consistente, chips de estado con color semántico, estado vacío ilustrado donde corresponda.
3. Confirmar cero regresión de datos (los mismos montos/estados que antes del restyle).
4. Gate final: los 7 test suites existentes en verde, `npm run build` sin errores.

## Sources

| Type | Reference | Detail |
| --- | --- | --- |
| Spec | sistema-visual | .nybo/plans/rediseno-ux-ui/specs/sistema-visual/spec.md — provee el tema y los 3 componentes compartidos que esta spec consume. |
| Spec | rediseno-ux-ui | .nybo/plans/rediseno-ux-ui/plan.md — feature-level, split rationale. |

## History

| # | Date | Event | Verdict | Summary |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | Spec created — 4 tasks, 6 test cases. |
| 2 | 2026-09-23 | build | ready | T1–T4 implementados, 170/170 tests verdes, 0 regresión. TC-005 redirigido de Suscripciones (sin flujo de alta propio) a Tarjetas — ver `evidence/decisions.yaml` D001. Coverage y live evidence diferidos (ver D002 y `build-results.md`). |
