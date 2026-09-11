# Autenticación — Frontend

## Intention

### What
Agrega pantallas de login y registro a taskia, y reemplaza el `usuarioId` generado al azar en cada carga por una sesión real basada en el JWT del backend de auth.

### Why
Hoy la app genera un UUID nuevo en cada carga de página y lo usa como identidad — no hay sesión real ni forma de que la misma persona vuelva a entrar a sus casas. Sin esto, el backend de autenticación (`auth-backend`) no tiene ninguna forma de usarse desde la UI.

## Solution
Dos pantallas nuevas (Login, Registro) construidas con el mismo sistema de diseño de `ui-modernization` (Material UI). Tras loguearse, el JWT se guarda y se envía en cada request a la API en vez del header `X-Usuario-Id`. Si el usuario pertenece a más de una casa, elige con cuál trabajar antes de entrar al shell existente.
See **[Solution Overview](feat/00-overview.md)** for the full architecture, data model, contracts, and UX/UI.

## Outcome
Una persona abre taskia, se registra o inicia sesión, y entra a sus casas reales — la misma persona que vuelve más tarde ve las mismas casas y datos, no una identidad nueva cada vez. Puede cerrar sesión y volver a entrar sin perder nada.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un usuario no autenticado debe ver una pantalla de login al abrir la app. | Sin un JWT válido guardado, la app nunca muestra el shell existente (Inicio/Miembros/etc.) directamente. |
| REQ-002 | Un usuario debe poder registrarse desde la UI indicando nombre, email y contraseña. | Un registro exitoso lleva directo al login (o auto-loguea), nunca deja al usuario en un estado ambiguo. |
| REQ-003 | Tras un login exitoso, el JWT recibido debe enviarse en cada request subsiguiente a la API, reemplazando el header `X-Usuario-Id` actual. | El JWT se guarda en el cliente (localStorage) y sobrevive a un refresh de página; una respuesta 401 de la API fuerza el logout y vuelve a mostrar el login. |
| REQ-004 | Un usuario logueado que pertenece a más de una Casa debe poder elegir con cuál trabajar, o crear una nueva. | La lista de casas del usuario se obtiene de la API (backend de `auth-backend`/`casas-miembros`); elegir una casa navega al shell existente para esa casa específica. |
| REQ-005 | Un usuario debe poder cerrar sesión. | Cerrar sesión borra el JWT guardado y vuelve a mostrar la pantalla de login. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** ningún JWT guardado **When** se abre la app **Then** se muestra la pantalla de Login, no el shell existente | `[UNIT]` |
| TC-002 (REQ-002) | **Given** datos de registro válidos **When** se completa el formulario de Registro **Then** se llama a `POST /auth/registro` y el usuario termina en la pantalla de Login | `[UNIT]` |
| TC-003 (REQ-003) | **Given** un login exitoso **When** se realiza cualquier request posterior a la API **Then** el header `Authorization: Bearer <jwt>` está presente, sin `X-Usuario-Id` | `[UNIT]` |
| TC-004 (REQ-003) | **Given** un JWT guardado inválido/expirado **When** la API responde 401 **Then** la app hace logout automático y vuelve a mostrar Login | `[UNIT]` |
| TC-005 (REQ-004) | **Given** un usuario logueado con 2 casas **When** entra a la app **Then** ve un selector de casas y puede elegir una | `[UNIT]` |
| TC-006 (REQ-005) | **Given** un usuario logueado **When** hace clic en "Cerrar sesión" **Then** el JWT guardado se borra y se muestra Login | `[UNIT]` |
| TC-007 (REQ-001..004) | **Given** un usuario nuevo **When** se registra, inicia sesión, crea una casa y navega el shell existente **Then** todo el flujo funciona de punta a punta en un navegador real | `[E2E]` |

## Sources

| Type | Reference | Location |
|---|---|---|
| Session | Pedido del usuario: login + creación/gestión de usuarios | Capturado en esta conversación, 2026-09-11. |
| Spec | auth-backend | .nybo/plans/usuarios-auth/specs/auth-backend/spec.md |
| Spec | ui-modernization | .nybo/plans/ui-modernization/spec.md |
