# Perfil con avatar - Technical Specification

| | |
| --- | --- |
| Progress | [progress.md](progress.md) |

## Intention

### What
Reemplaza el `Avatar` con inicial de cada miembro en Miembros/Ranking por su avatar Lottie + accesorios equipados, y agrega una pantalla "Mi Avatar" (elegir raza desbloqueada, comprar/equipar accesorios) dentro del grupo "Casa" de la navegación existente.

### Why
`avatares-economia` y `tienda-accesorios` construyeron toda la mecánica (créditos, catálogo, selección, compra, equipamiento) pero sin ningún lugar donde un miembro real la vea o la use — esta spec es la integración visual que hace tangible el pedido original del usuario.

## Outcome
Un miembro entra a Miembros o Ranking y ve, en vez de un círculo con su inicial, su perro/gato animado con la ropa que eligió puesta. Entra a "Mi Avatar" (dentro del menú "Casa"), ve su saldo de créditos, elige entre las razas que su nivel desbloqueó, y compra/equipa accesorios de la tienda — todo sin que el bottom nav mobile gane un ítem nuevo de primer nivel.

## Requirements

### REQ-001: Avatar visible en Miembros y Ranking
Las tarjetas de perfil de Miembros.tsx y las filas de Ranking.tsx muestran el `LottieAvatar` del miembro (raza seleccionada) con sus accesorios equipados superpuestos como overlay — reemplazando el `Avatar` con inicial actual. Un miembro sin avatar seleccionado (dato preexistente a esta feature) sigue mostrando el `Avatar` con inicial como respaldo.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-001 | **Given** un miembro con avatar y accesorios equipados **When** se renderiza su tarjeta en Miembros **Then** se muestra `LottieAvatar` con los overlays de sus accesorios equipados, no el `Avatar` con inicial. | `[UNIT]` |
| TC-002 | **Given** un miembro sin avatar seleccionado **When** se renderiza su tarjeta **Then** se muestra el `Avatar` con inicial (respaldo), sin romper por falta de dato. | `[UNIT]` |
| TC-003 | **Given** Ranking.tsx **When** se renderiza una fila de miembro **Then** también muestra su avatar, mismo patrón que Miembros. | `[UNIT]` |

### REQ-002: Pantalla "Mi Avatar"
Nueva pantalla `MiAvatar.tsx` que muestra el saldo de créditos del miembro, las razas de avatar desbloqueadas (seleccionables) y bloqueadas (con indicación de qué nivel se necesita), y la tienda de accesorios (comprar/equipar) filtrada por la especie del avatar actual.

- Seleccionar una raza desbloqueada la aplica de inmediato (sin paso de confirmación adicional, mismo criterio de "sin fricción" ya usado en el resto de la app).
- Comprar un accesorio actualiza el saldo de créditos mostrado en la misma pantalla, sin recargar.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-004 | **Given** la pantalla "Mi Avatar" **When** se renderiza **Then** muestra las razas desbloqueadas como seleccionables y las bloqueadas con el nivel requerido visible. | `[UNIT]` |
| TC-005 | **Given** esa pantalla **When** el miembro selecciona una raza desbloqueada **Then** se llama a `seleccionarAvatar` y la pantalla refleja el nuevo avatar activo. | `[INTEGRATION]` |
| TC-006 | **Given** la sección de tienda de esa pantalla **When** el miembro compra y equipa un accesorio **Then** el saldo de créditos mostrado baja su precio y el accesorio aparece equipado, sin recargar la pantalla. | `[INTEGRATION]` |

### REQ-003: Navegación sin nuevo ítem de primer nivel
"Mi Avatar" se agrega DENTRO del grupo "Casa" ya existente (`GRUPOS_DESKTOP`, junto a Miembros/Ranking/Actividad) — el bottom nav mobile sigue mostrando exactamente 4 ítems de primer nivel (Inicio, Casa, Gastos, Tareas), sin reintroducir el problema de overflow ya corregido (`fix nav-mobile-agrupada`).

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-007 | **Given** `AppNav.tsx` tras esta spec **When** se renderiza en mobile o desktop **Then** el grupo "Casa" incluye "Mi Avatar" junto a Miembros/Ranking/Actividad, y el bottom nav mobile sigue mostrando exactamente 4 ítems de primer nivel. | `[UNIT]` |

## Constraints
- REQ-001: ningún cambio a la lógica de datos/permisos de Miembros.tsx/Ranking.tsx — esta spec solo agrega la representación visual del avatar, mismo criterio "cero regresión funcional" ya aplicado en `rediseno-ux-ui`.
- REQ-003: `SECCIONES`/`GRUPOS_DESKTOP` (`AppNav.tsx`) se extienden agregando `"miAvatar"` al grupo `"Casa"` existente — nunca como una entrada `"suelta"` nueva ni un grupo nuevo.

## Solution
Se integra el avatar+accesorios en las 2 pantallas de perfil ya existentes, y se agrega una pantalla nueva anidada en la navegación existente — sin tocar el bottom nav ni la lógica de negocio de ninguna de las specs anteriores.

### Task Execution

| Task | File | Description | Dependencies |
| --- | --- | --- | --- |
| T1 | [01-plan-01-avatar-en-perfiles.md](feat/01-plan-01-avatar-en-perfiles.md) | Avatar+accesorios en Miembros/Ranking | — |
| T2 | [01-plan-02-pantalla-mi-avatar.md](feat/01-plan-02-pantalla-mi-avatar.md) | Pantalla "Mi Avatar" + navegación | — |

### Verification

| Task | Test cases | Additional gate criteria |
| --- | --- | --- |
| T1 | TC-001, TC-002, TC-003 | `[AUTO]` `Miembros.test.tsx` y `Ranking.test.tsx` en verde. |
| T2 | TC-004, TC-005, TC-006, TC-007 | `[AUTO]` `AppShell.test.tsx` sigue en verde (4 ítems de primer nivel, sin regresión). |

#### Outcome Smoke Test
1. Con un miembro que ya seleccionó un avatar y equipó accesorios, entrar a Miembros — confirmar que se ve el avatar animado con la ropa puesta.
2. Entrar a "Mi Avatar" (dentro de "Casa"), elegir una raza distinta desbloqueada — confirmar que Miembros refleja el cambio.
3. Comprar y equipar un accesorio nuevo desde esa pantalla — confirmar que el saldo de créditos baja y el accesorio queda equipado.
4. Confirmar en mobile que el bottom nav sigue mostrando 4 ítems (no 5).
5. Gate final: los 4 test suites existentes/nuevos en verde, `npm run build` sin errores.

## Sources

| Type | Reference | Detail |
| --- | --- | --- |
| Spec | avatares-economia | .nybo/plans/personalizacion-avatares/specs/avatares-economia/spec.md — provee `avatarClient.ts`/`LottieAvatar`. |
| Spec | tienda-accesorios | .nybo/plans/personalizacion-avatares/specs/tienda-accesorios/spec.md — provee la mecánica de tienda que esta pantalla expone. |
| Spec | rediseno-ux-ui/pantallas-casa | .nybo/plans/rediseno-ux-ui/specs/pantallas-casa/spec.md — define las tarjetas de perfil de Miembros/Ranking que esta spec extiende. |
| Spec | personalizacion-avatares | .nybo/plans/personalizacion-avatares/plan.md — feature-level, split rationale. |

## History

| # | Date | Event | Verdict | Summary |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | Spec created — 2 tasks, 7 test cases. |
| 2 | 2026-09-23 | build | verified | T1+T2 implementados; verify spec-level en verde (build/lint/tests/live evidence). Ver evidence/1/build-results.md. |
