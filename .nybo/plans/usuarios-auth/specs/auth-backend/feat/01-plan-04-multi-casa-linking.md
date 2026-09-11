# Task 4 — crear_casa/agregar_miembro vinculan al Usuario real

## Scope
- `src/services/casa_service.py` — `crear_casa`, agrega `listar_casas_de_usuario`.
- `src/services/miembro_service.py` — `agregar_miembro`.
- `src/api/routes/casas.py` — `GET /casas/mias` (nuevo).
- `src/api/schemas.py` — `MiembroCreate` agrega `email` en vez de aceptar un id de miembro arbitrario.

## Changes
### Service Logic
- `crear_casa(nombre, usuario_id)`: el Miembro-administrador creado queda con `usuario_id=usuario_id` (el del token, ya no un UUID arbitrario) — TC-007.
- `agregar_miembro(casa_id, nombre, identificacion, email_usuario, actor)`: en vez de crear un Miembro "suelto", busca el `Usuario` existente por `email_usuario` (404 si no existe — un usuario debe registrarse antes de que lo agreguen a una casa) y vincula el nuevo Miembro a su `usuario_id` — TC-008. Firma cambia: agrega el parámetro `email_usuario`.
- Un mismo `usuario_id` puede tener múltiples filas `Miembro` (una por Casa) — ya soportado por el esquema de T1, esta task es la que efectivamente lo ejercita.
- `listar_casas_de_usuario(usuario_id)`: devuelve las Casas donde el usuario tiene un Miembro activo (join `miembros.usuario_id` → `casas`) — expuesto vía `GET /casas/mias` (TC-010), la única ruta de descubrimiento de casas por usuario que existe en el proyecto.

## Design Rationale
Requerir que el Usuario ya exista (por email) antes de agregarlo a una casa —en vez de crear una identidad al vuelo— es lo que hace real la regla "un Usuario puede estar en varias Casas": todas sus membresías apuntan al mismo registro de Usuario, nunca a uno nuevo por casa.

## Dependencies
T3 (rutas ya migradas a JWT — este task ajusta la lógica que esas rutas invocan).

## Done When
- [ ] TC-007, TC-008, TC-010 pasan.
- [ ] Un Usuario que crea 2 casas tiene 2 filas Miembro, ambas con su mismo `usuario_id`.
- [ ] Build succeeds.

## Interfaces Produced
- `{name: "listar_casas_de_usuario", signature: "(usuario_id: UUID) -> Casa[]", kind: "function"}`

## Standalone Verifiable
Sí, una vez T3 existe.
