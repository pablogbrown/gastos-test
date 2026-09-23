# Auth y onboarding - Technical Specification

| | |
| --- | --- |
| Progress | [progress.md](progress.md) |

## Intention

### What
Aplica el sistema visual de `sistema-visual` a las 4 pantallas de autenticación y onboarding: Login, Registro, Selector de casas y Crear casa.

### Why
Estas 4 pantallas son la primera impresión de la app para cualquier usuario nuevo — hoy son formularios sin ningún tratamiento visual particular. Al ser el contexto de un actor distinto (usuario no autenticado, sin datos propios que mostrar todavía), su patrón de diseño es de formulario centrado, no de lista — se separan del resto del rediseño por ese eje real, no por conveniencia de agrupación.

## Outcome
Login y Registro muestran una tarjeta de autenticación centrada con el nombre "taskia" como identidad de marca, usando la nueva paleta. Selector de casas y Crear casa siguen el mismo lenguaje visual centrado. Todos los mensajes de error/validación existentes se preservan exactamente igual.

## Requirements

### REQ-001: Login y Registro con identidad de marca
Login y Registro muestran una tarjeta (`Card`) centrada en la pantalla (no un formulario a ancho completo), con el nombre "taskia" como encabezado de marca, usando la paleta y tipografía del nuevo tema. Todos los campos, validaciones y mensajes de error existentes se preservan sin cambio de comportamiento.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-001 | **Given** la pantalla Login **When** se renderiza **Then** el formulario está contenido en una tarjeta centrada con el nombre "taskia" visible como encabezado. | `[UNIT]` |
| TC-002 | **Given** un intento de login con credenciales inválidas **When** el backend responde error **Then** el mensaje de error se muestra exactamente igual que antes del restyle (mismo texto, mismo rol accesible). | `[INTEGRATION]` |

### REQ-002: Selector de casas y Crear casa consistentes
Selector de casas y Crear casa adoptan el mismo layout centrado y la misma paleta que Login/Registro — un usuario recién autenticado no percibe un salto visual entre "iniciar sesión" y "elegir/crear una casa".

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-003 | **Given** un usuario con más de una casa **When** se renderiza el Selector de casas **Then** cada casa se muestra como una tarjeta seleccionable, con el mismo lenguaje visual (radio/esquinas/paleta) que Login/Registro. | `[UNIT]` |

### REQ-003: Cero regresión funcional
Ninguna validación de formulario, ningún flujo de JWT/sesión, ni ningún cliente de API (`authClient.ts`, `casasClient.ts`) cambia — el restyle es puramente de presentación en las 4 pantallas.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-004 | **Given** el test suite existente de las 4 pantallas (`Login.test.tsx`, `Registro.test.tsx`, `SelectorCasas.test.tsx`) y `CrearCasa` (sin test dedicado hoy — cubierta indirectamente) **When** se corre tras el restyle **Then** los suites existentes pasan sin modificar sus queries por rol/label. | `[INTEGRATION]` |

## Constraints
- REQ-001/002: reutilizan exclusivamente el tema de `sistema-visual` — no se introduce ningún logo/imagen externa (fuera de scope, ver Out of Scope); "taskia" se muestra como texto con la tipografía del tema.
- REQ-003: ningún archivo bajo `src/services/`, `src/api/`, o `src/db/` se modifica, ni `authClient.ts`/`casasClient.ts` cambian de firma — exclusivamente frontend de presentación.

## Solution
Se aplica el mismo layout centrado (tarjeta + fondo del tema) a las 4 pantallas, agrupadas en 2 tasks: Login+Registro (mismo patrón exacto, formulario de credenciales) y Selector de casas+Crear casa (mismo patrón exacto, selección/alta de casa).

### Task Execution

| Task | File | Description | Dependencies |
| --- | --- | --- | --- |
| T1 | [01-plan-01-login-registro.md](feat/01-plan-01-login-registro.md) | Login + Registro | — |
| T2 | [01-plan-02-selector-crear-casa.md](feat/01-plan-02-selector-crear-casa.md) | Selector de casas + Crear casa | — |

### Verification

| Task | Test cases | Additional gate criteria |
| --- | --- | --- |
| T1 | TC-001, TC-002, TC-004 | `[AUTO]` `Login.test.tsx` y `Registro.test.tsx` en verde. |
| T2 | TC-003, TC-004 | `[AUTO]` `SelectorCasas.test.tsx` en verde. |

#### Outcome Smoke Test
1. Cerrar sesión, navegar a Login y Registro.
2. Confirmar visualmente: tarjeta centrada, nombre "taskia" como encabezado, paleta consistente con el resto de la app.
3. Loguearse con un usuario de más de una casa, confirmar el Selector de casas con el mismo lenguaje visual.
4. Gate final: los test suites existentes en verde, `npm run build` sin errores.

## Sources

| Type | Reference | Detail |
| --- | --- | --- |
| Spec | sistema-visual | .nybo/plans/rediseno-ux-ui/specs/sistema-visual/spec.md — provee el tema. |
| Spec | rediseno-ux-ui | .nybo/plans/rediseno-ux-ui/plan.md — feature-level, split rationale. |

## History

| # | Date | Event | Verdict | Summary |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | Spec created — 2 tasks, 4 test cases. |
