# Autenticación — Backend

## Intention

### What
Agrega un Usuario global (email + contraseña) con registro y login vía JWT, y reemplaza el header placeholder `X-Usuario-Id` por autenticación real en las 4 specs ya shippeadas (casas-miembros, gastos, tareas-puntos, dashboard-actividad).

### Why
Hoy cualquiera puede enviar cualquier UUID como `X-Usuario-Id` y actuar como esa persona — no hay identidad real. Sin login, taskia no puede exponerse fuera de un entorno de desarrollo/demo.

## Solution
Un Usuario global (tabla nueva) con contraseña hasheada; `POST /auth/registro` y `POST /auth/login` (este último emite un JWT). Las rutas existentes dejan de leer `X-Usuario-Id` y en cambio decodifican el JWT del header `Authorization` para resolver el Usuario autenticado, y desde ahí el Miembro correspondiente dentro de la casa sobre la que se opera. Un Usuario puede tener un Miembro en más de una Casa.
See **[Solution Overview](feat/00-overview.md)** for the full architecture, data model, contracts, and UX/UI.

## Outcome
Nadie puede operar sobre una casa sin haberse registrado y logueado primero, y cada acción queda atribuida a un Usuario real — no a un UUID inventado por el cliente. Las reglas de negocio existentes (roles, balance, puntos) siguen funcionando exactamente igual, ahora sobre una identidad real.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un usuario debe poder registrarse indicando email y contraseña. | La contraseña se almacena hasheada (nunca en texto plano); el email debe ser único entre todos los Usuarios. |
| REQ-002 | Un usuario registrado debe poder loguearse con email y contraseña, recibiendo un JWT. | Credenciales inválidas (email inexistente o contraseña incorrecta) responden 401 con el mismo mensaje genérico en ambos casos, para no revelar qué emails existen. |
| REQ-003 | Todas las rutas de casas, gastos, tareas y dashboard que hoy leen `X-Usuario-Id` deben en cambio resolver al actor a partir de un JWT válido en el header `Authorization`. | Un request sin JWT válido a cualquiera de esas rutas responde 401, reemplazando el comportamiento actual (header ausente = 422 de validación). |
| REQ-004 | Un Usuario puede pertenecer a más de una Casa, con un Miembro distinto por cada una. | `crear_casa` vincula al Miembro-administrador creado con el `usuario_id` del token; `agregar_miembro` vincula el nuevo Miembro a un Usuario existente identificado por su email, no por un UUID que el cliente inventa. |
| REQ-005 | Un usuario autenticado que no es miembro de una casa determinada no debe poder operar sobre ella, incluso con un JWT válido de otro usuario legítimo. | Se resuelve el Miembro del Usuario autenticado dentro de esa Casa específica; si no existe uno activo, la ruta responde 403 — mismo `requiere_membresia_activa` de `casas-miembros`, ahora alimentado por el Usuario del JWT en vez del header crudo. |
| REQ-006 | Un usuario autenticado debe poder consultar la lista de casas en las que tiene un Miembro activo. | No existía ninguna ruta para esto antes de esta spec (las rutas existentes solo operan sobre una casa ya conocida por id); es lo que permite a un cliente (ej. un selector de casas) descubrir con cuáles casas puede trabajar un usuario. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** datos de registro válidos **When** `POST /auth/registro` **Then** se crea el Usuario con la contraseña hasheada, nunca en texto plano | `[UNIT]` |
| TC-002 (REQ-001) | **Given** un email ya registrado **When** `POST /auth/registro` con ese mismo email **Then** se rechaza con 409 | `[UNIT]` |
| TC-003 (REQ-002) | **Given** un usuario registrado **When** `POST /auth/login` con credenciales correctas **Then** responde 200 con un JWT válido | `[UNIT]` |
| TC-004 (REQ-002) | **Given** credenciales incorrectas (o un email inexistente) **When** `POST /auth/login` **Then** responde 401 con el mismo mensaje en ambos casos | `[UNIT]` |
| TC-005 (REQ-003) | **Given** un request sin JWT (o con uno inválido) a una ruta antes protegida por `X-Usuario-Id` **When** se envía **Then** responde 401 | `[INTEGRATION]` |
| TC-006 (REQ-003) | **Given** un JWT válido **When** se llama a una ruta migrada (ej. `POST /casas`) **Then** el actor se resuelve correctamente desde el token, con el mismo comportamiento de negocio que antes | `[INTEGRATION]` |
| TC-007 (REQ-004) | **Given** un Usuario que crea dos casas distintas **When** se consulta cada una **Then** tiene un Miembro propio en cada una, ambos vinculados al mismo `usuario_id` | `[INTEGRATION]` |
| TC-008 (REQ-004) | **Given** un administrador que agrega un miembro indicando el email de un Usuario existente **When** se registra el alta **Then** el nuevo Miembro queda vinculado al `usuario_id` de ese Usuario | `[UNIT]` |
| TC-009 (REQ-005) | **Given** un Usuario autenticado que no es miembro de la Casa X **When** intenta operar sobre la Casa X **Then** responde 403 | `[INTEGRATION]` |
| TC-010 (REQ-006) | **Given** un Usuario con Miembro activo en 2 casas y ninguno en una tercera **When** `GET /casas/mias` **Then** devuelve exactamente esas 2 casas | `[UNIT]` |

## Sources

| Type | Reference | Location |
|---|---|---|
| Session | Pedido del usuario: login + creación/gestión de usuarios | Capturado en esta conversación, 2026-09-11. Decisiones confirmadas: Usuario global multi-casa, email+contraseña con JWT, auto-registro abierto. |
| Spec | gestion-domestica | .nybo/plans/gestion-domestica/plan.md |
