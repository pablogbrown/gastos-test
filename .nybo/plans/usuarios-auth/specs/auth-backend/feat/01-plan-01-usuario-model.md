# Task 1 — Data Layer: Usuario y FK Miembro.usuario_id

## Scope
- `src/db/models/usuario.py` — modelo Usuario.
- `src/db/models/miembro.py` — agrega columna `usuario_id` (FK, nullable).
- `src/db/migrations/0005_usuarios.py` — migración nueva.
- `requirements.txt` — agrega `pyjwt`, `bcrypt`.

## Changes
### Data Layer
- Tabla `usuarios`: id (uuid pk), email (string, unique, not null), password_hash (string, not null), nombre (string, nullable), creado_en (timestamp).
- `miembros.usuario_id`: nueva columna FK → `usuarios.id`, nullable (para no romper filas ya sembradas manualmente en pruebas previas), pero toda alta nueva vía `crear_casa`/`agregar_miembro` (T4) la completa siempre.
- Índice único en `usuarios.email`.

## Design Rationale
Separar Usuario (identidad global) de Miembro (rol dentro de una casa) preserva la relación 1-a-N ya implícita en la regla original del documento ("una persona puede participar en más de una casa") sin reescribir el modelo de Miembro existente — solo se le agrega una FK.

## Dependencies
Ninguna — primer task de la spec.

## Done When
- [ ] La migración 0005 corre limpia sobre una base con las 4 migraciones anteriores ya aplicadas.
- [ ] `usuarios.email` rechaza duplicados a nivel de constraint.
- [ ] `pyjwt`/`bcrypt` instalados y disponibles.

## Interfaces Produced
- `{name: "Usuario", signature: "class Usuario(id, email, password_hash, nombre, creado_en)", kind: "class"}`

## Standalone Verifiable
Sí — el esquema y sus constraints se pueden probar sin la capa de servicio.
