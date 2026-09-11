# Modernización de la UI

## Intention

### What
Rediseña las 8 pantallas existentes de taskia y su navegación con Material UI, para que la app se vea moderna y sea usable en un celular Android sin esfuerzo.

### Why
La UI actual es HTML plano sin estilos, con una fila de botones como navegación — no es utilizable cómodamente en mobile y no transmite un producto terminado. Esto bloquea que cualquier usuario real (no solo quien la construyó) la use desde su teléfono.

## Solution
Se introduce Material UI (MUI) como sistema de componentes y tema, con un `ThemeProvider` global. La navegación pasa de la fila de botones actual a un patrón responsivo: bottom tab bar (`BottomNavigation`) en viewports angostos, barra superior en desktop. Cada pantalla existente se reconstruye sobre componentes MUI en vez de HTML nativo sin estilo.
See **[Solution Overview](feat/00-overview.md)** for the full architecture, data model, contracts, and UX/UI.

## Outcome
Cualquier persona abre taskia desde su celular Android y la usa con la misma fluidez que una app nativa: navegación por pestañas inferiores, formularios y listas legibles sin hacer zoom, sin scroll horizontal, y con el mismo comportamiento funcional de hoy (nada de lo que ya funciona deja de funcionar).

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Toda pantalla debe ser usable en un viewport mobile típico de Android (360×800) sin scroll horizontal ni elementos cortados. | Se valida contra ese viewport específicamente, no solo "responsive en general". |
| REQ-002 | La navegación principal debe mostrarse como bottom tab bar en viewports angostos (mobile) y como barra superior en viewports anchos (desktop), cubriendo las mismas 7 secciones ya existentes (Inicio, Miembros, Gastos, Balance, Tareas, Ranking, Actividad). | El breakpoint que decide entre ambos patrones es el que MUI expone por defecto (`sm`, 600px) — no se define uno custom sin motivo. |
| REQ-003 | Todos los componentes visuales (botones, campos de formulario, tablas, listas) deben construirse con componentes de Material UI, con un tema (colores, tipografía) consistente en toda la app. | Ningún elemento HTML nativo sin estilo (`<button>`, `<input>` plano) debe quedar en las 8 pantallas rediseñadas. |
| REQ-004 | Los elementos interactivos de la navegación deben tener un área táctil de al menos 44×44px, según la guía estándar de accesibilidad táctil. | Se configura a nivel de tema/estilo de los componentes de navegación, no se deja al default de MUI sin verificar. |
| REQ-005 | El comportamiento funcional de las 8 pantallas (qué datos muestran, qué acciones disparan, a qué endpoint llaman) no debe cambiar — solo su presentación visual. | La suite de tests de frontend existente debe seguir demostrando el mismo comportamiento tras el restyle, adaptada a la nueva estructura de componentes cuando haga falta. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-002) | **Given** un viewport angosto (< 600px) **When** se renderiza el shell de la app **Then** la navegación se muestra como `BottomNavigation` con las 7 secciones | `[UNIT]` |
| TC-002 (REQ-002) | **Given** un viewport ancho (≥ 600px) **When** se renderiza el shell de la app **Then** la navegación se muestra como barra superior, no como bottom tab bar | `[UNIT]` |
| TC-003 (REQ-003) | **Given** cualquiera de las 8 pantallas rediseñadas **When** se renderiza **Then** usa componentes de Material UI (verificable por sus clases/roles) en vez de elementos HTML nativos sin estilo | `[UNIT]` |
| TC-004 (REQ-004) | **Given** el tema configurado para los ítems de `BottomNavigation` **When** se inspeccionan sus estilos **Then** el alto mínimo configurado es de al menos 44px | `[UNIT]` |
| TC-005 (REQ-005) | **Given** la suite de tests de frontend existente (comportamiento de las 8 pantallas) **When** corre después del restyle **Then** seguir pasando sin pérdida de cobertura de comportamiento | `[UNIT]` |
| TC-006 (REQ-001) | **Given** un viewport de celular Android real (360×800) y la pantalla de Gastos con varios gastos listados **When** se visualiza en un navegador real **Then** no hay scroll horizontal y todos los elementos son legibles y clickeables | `[E2E]` |

## Sources

| Type | Reference | Location |
|---|---|---|
| Session | Pedido del usuario: UI moderna, responsiva y compatible con Android | Capturado en esta conversación, 2026-09-11. Decisiones confirmadas: Material UI, bottom tab bar mobile, sin pantallas de login (las agrega la spec de Auth después). |
