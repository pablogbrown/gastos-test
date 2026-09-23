# Sistema visual - Technical Specification

| | |
| --- | --- |
| Progress | [progress.md](progress.md) |

## Intention

### What
Reemplaza la identidad visual genérica de MUI (paleta índigo/teal por defecto, esquinas de 4px, fondo gris plano) por un sistema de diseño propio y distintivo — paleta, tipografía, forma y elevación coherentes — y crea 3 componentes compartidos (`PageHeader`, `StatCard`, `EmptyState`) que el resto del rediseño (pantallas-financieras, pantallas-casa, auth-onboarding) va a reutilizar. Se aplica primero al shell de navegación y a Inicio, como pantalla bandera.

### Why
El usuario, tras ver la app corriendo (web y Android), calificó el diseño actual de "viejo, poco atractivo". La feature `ui-modernization` (2026-09-11) resolvió la navegación responsiva y la base de componentes MUI, pero dejó la paleta y tipografía por defecto de MUI sin personalizar — el problema ahora es puramente de identidad visual, no de framework.

## Outcome
Al abrir la app, el usuario ve una paleta cálida y distintiva (no el índigo/teal genérico de MUI), tipografía con jerarquía clara, tarjetas con esquinas redondeadas y sombra suave en vez de fondo plano, y una barra de navegación con el ítem activo claramente destacado. La pantalla Inicio, reconstruida con estos componentes, sirve de referencia visual para el resto de las pantallas.

## Requirements

### REQ-001: Tema visual distintivo
El tema único de la app (`src/frontend/theme.ts`, consumido vía el `ThemeProvider` ya existente) define una paleta propia (primario, secundario, y colores semánticos para estados como pagado/a_pagar/pendiente/rechazado), una escala tipográfica con jerarquía clara (h1-h6, body1/body2, caption, con pesos definidos), radio de esquina aumentado (12-16px) y sombras suaves de elevación — reemplazando los valores por defecto de MUI. Ninguna pantalla define paleta o tipografía propia.

- Los números monetarios usan `font-variant-numeric: tabular-nums` para alinearse en columnas.
- El radio de esquina y la elevación se definen una sola vez en `theme.ts` (`shape.borderRadius`, `components.MuiCard.styleOverrides`) — nunca repetidos inline en cada pantalla.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-001 | **Given** el tema exportado por `theme.ts` **When** se inspeccionan `palette.primary.main`, `palette.secondary.main` y `shape.borderRadius` **Then** ninguno coincide con los valores por defecto de MUI (`#3f51b5`/`#00897b`/4) ni con los valores actuales de `ui-modernization`. | `[UNIT]` |
| TC-002 | **Given** un componente `Card` renderizado bajo el nuevo tema **When** se inspecciona su estilo computado **Then** tiene `border-radius` ≥ 12px y una sombra de elevación (no `boxShadow: none`). | `[UNIT]` |

### REQ-002: Componentes compartidos reutilizables
Existen 3 componentes de presentación en `src/frontend/components/`: `PageHeader` (título, subtítulo opcional, acción primaria opcional), `StatCard` (ícono, valor destacado, etiqueta), y `EmptyState` (ícono, mensaje, acción opcional) — listos para que las specs `pantallas-financieras`, `pantallas-casa` y `auth-onboarding` los reutilicen sin reinventar el patrón en cada pantalla.

- Cada componente es puramente presentacional (props in, JSX out) — no llama a ningún cliente de API ni conoce lógica de negocio.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-003 | **Given** `<PageHeader title="Gastos" action={{label:"Nuevo", onClick}} />` **When** se renderiza **Then** el título es visible por rol de heading y el botón de acción dispara `onClick` al hacer click. | `[UNIT]` |
| TC-004 | **Given** `<EmptyState message="Sin gastos todavía" />` sin `action` **When** se renderiza **Then** muestra el ícono y el mensaje, sin ningún botón. | `[UNIT]` |
| TC-005 | **Given** `<StatCard label="Total" value="$50.000" />` **When** se renderiza **Then** ambos textos son visibles y el valor usa una tipografía de mayor peso/tamaño que la etiqueta (estilo computado). | `[UNIT]` |

### REQ-003: Shell de navegación restyled
`AppNav.tsx` adopta el nuevo tema — el ítem activo (mobile `BottomNavigation` y desktop `AppBar`/grupos) se destaca visualmente con el color primario nuevo, sin cambiar el breakpoint responsivo existente (`sm`, 600px) ni el ruteo de las 9 secciones/16 pantallas ya cableadas.

- Ningún test existente de `AppShell.test.tsx` cambia su forma de consulta (accesibilidad, no estructura) — ver convención de dominio ya establecida.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-006 | **Given** la pantalla activa es "Inicio" **When** se renderiza `AppNav` en mobile (`<sm`) **Then** el ítem "Inicio" de `BottomNavigation` tiene `aria-current="true"` o el estado `selected` de MUI activo. | `[UNIT]` |
| TC-007 | **Given** el mismo escenario en desktop (`≥sm`) **When** se renderiza `AppNav` **Then** el comportamiento de agrupación de `GRUPOS_DESKTOP` (botones sueltos + menús para "Casa"/"Gastos") sigue funcionando sin regresión — mismo test suite existente en verde. | `[INTEGRATION]` |

### REQ-004: Inicio como pantalla bandera
`InicioCasa.tsx` se reconstruye usando el nuevo tema y los 3 componentes compartidos (`PageHeader` para el encabezado, `StatCard` para balance/resumen, `EmptyState` donde hoy no hay ninguno — p.ej. sin gastos recientes) preservando el 100% de sus datos y lógica actuales (los banners de alerta de tarjetas/mantenimiento, el mini-ranking, la meta de la casa).

- Ningún cliente de API (`dashboardClient.ts`, etc.) cambia de firma ni de comportamiento — este REQ es puramente de presentación.

| ID | Given/When/Then | Type |
| --- | --- | --- |
| TC-008 | **Given** el dashboard actual con datos de balance, tarjetas con alerta, y ranking **When** se renderiza el nuevo `InicioCasa.tsx` **Then** toda la información que el test suite existente (`InicioCasa.test.tsx`) verifica sigue presente y accesible por los mismos roles/labels — cero regresión funcional. | `[INTEGRATION]` |
| TC-009 | **Given** una casa sin gastos recientes **When** se renderiza Inicio **Then** la sección de gastos recientes muestra `EmptyState` en vez de una lista vacía sin mensaje. | `[UNIT]` |

## Constraints

- REQ-001: la paleta y tipografía se definen una sola vez en `theme.ts` — ninguna pantalla (de esta spec ni de las 3 siguientes) puede sobreescribir color/tipografía vía `sx` ad-hoc salvo un caso puntual documentado.
- REQ-002: los 3 componentes compartidos no pueden importar ningún cliente de API (`src/frontend/api/*`) — mantenerlos puramente presentacionales es lo que permite reutilizarlos en las 3 specs siguientes sin acoplarlos a un dominio.
- REQ-003: el breakpoint `sm` y las 16 rutas ya cableadas en `App.tsx`/`AppNav.tsx` no cambian — este REQ es de estilo, no de estructura de navegación.
- REQ-004: cero cambios en `dashboard_service.py` ni en ningún cliente de API — este REQ es puramente de presentación en el frontend.

## Solution
Se define un nuevo tema "Cálido minimal" en `theme.ts`, se construyen 3 componentes de presentación compartidos, y se aplican ambos al shell de navegación y a Inicio como demostración. El resto de las pantallas (specs siguientes) consumen exactamente estos mismos artefactos — nada nuevo se inventa fuera de esta spec.

### Open Decisions

#### D-01: Dirección visual del nuevo tema
- **Opción A — Cálido minimal**: fondo off-white cálido, un único color primario (verde/teal profundo, evoca "hogar" sin perder seriedad financiera), radio de esquina generoso (16px), sombras suaves. Menor riesgo de implementación sobre el setup MUI v9 actual.
- **Opción B — Fintech bold**: primario azul marino oscuro, acento naranja de alto contraste para CTAs, esquinas más angulares (8px). Transmite "app financiera" pero pierde la calidez de "app de hogar" (la app también maneja tareas domésticas y mantenimiento, no es solo finanzas).
- **Opción C — Material 3 tonal**: paleta tonal derivada de un color semilla (estilo Material You), superficies con elevación dinámica. Mayor fidelidad a las guías actuales de Material Design, pero requiere `CssVarsProvider`/tokens tonales que MUI v9 en este proyecto no usa hoy — mayor riesgo de introducir bugs de tipado (ver gotchas de `Stack`/`Menu` ya registrados en `frontend.md`).

**Status:** resuelto automáticamente (nivel de confianza semi-autonomous, sin `--discuss`).
- [x] A — Cálido minimal
- [ ] B — Fintech bold
- [ ] C — Material 3 tonal

**Rationale:** taskia es una app de hogar (gastos + tareas + mantenimiento), no solo financiera — la calidez de la Opción A encaja mejor que el tono "fintech" de B. Además, A es la de menor riesgo de implementación sobre el MUI v9 ya instalado (sin tocar `CssVarsProvider`), evitando repetir los gotchas de tipado ya registrados en `frontend.md` para este mismo major de MUI.

### Task Execution

| Task | File | Description | Dependencies |
| --- | --- | --- | --- |
| T1 | [01-plan-01-theme-tokens.md](feat/01-plan-01-theme-tokens.md) | Nuevo tema en `theme.ts`: paleta, tipografía, forma, elevación | — |
| T2 | [01-plan-02-shared-components.md](feat/01-plan-02-shared-components.md) | `PageHeader`, `StatCard`, `EmptyState` | T1 |
| T3 | [01-plan-03-nav-shell.md](feat/01-plan-03-nav-shell.md) | Restyle de `AppNav.tsx` | T1 |
| T4 | [01-plan-04-inicio-flagship.md](feat/01-plan-04-inicio-flagship.md) | Reconstruir `InicioCasa.tsx` | T1, T2 |

### Verification

| Task | Test cases | Additional gate criteria |
| --- | --- | --- |
| T1 | TC-001, TC-002 | `[AUTO]` `npm run build` compila sin errores de tipos tras el cambio de tema. |
| T2 | TC-003, TC-004, TC-005 | `[AUTO]` los 3 componentes exportan tipos de props documentados (TSDoc o interfaz nombrada). |
| T3 | TC-006, TC-007 | `[AUTO]` `AppShell.test.tsx` completo en verde sin modificar sus queries. |
| T4 | TC-008, TC-009 | `[AUTO]` `InicioCasa.test.tsx` completo en verde sin modificar sus queries; `[HUMAN]` smoke visual en el emulador Android confirmando que el nuevo diseño se ve como se espera. |

#### Outcome Smoke Test
1. Levantar el stack (`make up`), loguearse, entrar a Inicio.
2. Confirmar visualmente: paleta nueva (no índigo/teal por defecto), tarjetas con esquinas redondeadas y sombra, ítem de navegación activo destacado.
3. Confirmar que balance, alertas de tarjetas/mantenimiento, mini-ranking y meta de la casa siguen mostrando datos reales, sin ningún dato faltante respecto al diseño anterior.
4. Gate final: `npm run test` y `npm run build` en verde; ningún test pre-existente modificado en su forma de consulta.

## Sources

| Type | Reference | Detail |
| --- | --- | --- |
| Session | Captured from this conversation on 2026-09-23 | El usuario vio la app corriendo (web + Android vía Capacitor) y pidió un rediseño experto de UX/UI de todo el frontend, calificando el diseño actual de "viejo, poco atractivo". |
| Spec | ui-modernization | .nybo/plans/ui-modernization/spec.md — base MUI/navegación responsiva sobre la que este rediseño construye. |

## History

| # | Date | Event | Verdict | Summary |
| --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | Spec created — 4 tasks, 9 test cases. |
