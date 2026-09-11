# Task 2 — Service Layer: registro, login, hashing y JWT

## Scope
- `src/services/auth_service.py`
- `src/services/exceptions.py` — agrega `InvalidCredentialsError` si no existe un equivalente.

## Changes
### Service Logic
- `registrar_usuario(email, password, nombre)`: valida email único (TC-002), hashea la contraseña con `bcrypt` (nunca se persiste en texto plano, TC-001), crea el `Usuario`.
- `autenticar_usuario(email, password)`: busca el Usuario por email, verifica el hash; si no existe o no matchea, lanza `InvalidCredentialsError` (mismo mensaje en ambos casos, TC-004) — nunca revela cuál de las dos falló.
- `emitir_token(usuario_id)`: genera un JWT (`pyjwt`) con `sub=usuario_id` y expiración corta (24h), firmado con un secreto leído de variable de entorno (`JWT_SECRET`, con default de desarrollo si no está seteada — igual patrón que `DATABASE_URL` en `src/db/base.py`).
- `decodificar_token(token)`: verifica firma y expiración, devuelve el `usuario_id`; lanza `InvalidCredentialsError` si el token es inválido/expiró (TC-005).

## Design Rationale
Aislar hashing/JWT en su propio servicio (no mezclado con `casa_service`/`miembro_service`) mantiene el principio ya establecido en el proyecto (un servicio por responsabilidad, reutilizado por la capa de rutas).

## Dependencies
T1 (modelo Usuario).

## Done When
- [ ] TC-001, TC-002, TC-003, TC-004 pasan.
- [ ] La contraseña nunca aparece en texto plano en ningún log ni en la respuesta de la API.
- [ ] Build y tipos compilan.

## Interfaces Produced
- `{name: "registrar_usuario", signature: "(email: str, password: str, nombre: str | None) -> Usuario", kind: "function"}`
- `{name: "autenticar_usuario", signature: "(email: str, password: str) -> Usuario", kind: "function"}`
- `{name: "emitir_token", signature: "(usuario_id: UUID) -> str", kind: "function"}`
- `{name: "decodificar_token", signature: "(token: str) -> UUID", kind: "function"}`

## Standalone Verifiable
Sí, con T1 disponible.
