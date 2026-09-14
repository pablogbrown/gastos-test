# Task 3 — API Routes: /auth/* y migración de las 4 rutas existentes

## Scope
- `src/api/routes/auth.py` (nuevo).
- `src/api/routes/casas.py`, `src/api/routes/gastos.py`, `src/api/routes/tareas.py`, `src/api/routes/dashboard.py` — reemplazar `Header(..., alias="X-Usuario-Id")` por la nueva dependency de auth.
- `src/api/main.py` — registrar `auth_router`.
- `src/api/dependencies.py` (nuevo) — `get_current_usuario`.

## Changes
### API Route
- `auth_router`: `POST /auth/registro` → `registrar_usuario`; `POST /auth/login` → `autenticar_usuario` + `emitir_token`.
- `get_current_usuario(authorization: str = Header(...))` (`src/api/dependencies.py`): extrae el JWT del header `Authorization: Bearer <token>`, llama a `decodificar_token`, devuelve el `usuario_id`; sin header o token inválido → 401 (TC-005).
- Cada handler de `casas.py`/`gastos.py`/`tareas.py`/`dashboard.py` que hoy recibe `actor: UUID = Header(..., alias="X-Usuario-Id")` pasa a recibir `usuario_id: UUID = Depends(get_current_usuario)`, y resuelve el `Miembro` correspondiente a ese `usuario_id` dentro de la Casa de la ruta (reutilizando `requiere_membresia_activa`, ahora alimentado desde el Usuario resuelto — TC-006, TC-009).

## Design Rationale
Centralizar la extracción de identidad en una única dependency (`get_current_usuario`) evita duplicar la lógica de decodificación de JWT en cada uno de los 4 routers — cambia una vez, se propaga a todos.

## Dependencies
T2 (servicio de auth).

## Done When
- [ ] TC-005, TC-006, TC-009 pasan.
- [ ] Los 4 routers existentes ya no leen `X-Usuario-Id` en ningún handler.
- [ ] Build succeeds.

## Interfaces Produced
- `{name: "auth_router", signature: "APIRouter", kind: "export"}`
- `{name: "get_current_usuario", signature: "(authorization: str) -> UUID", kind: "function"}`

## Standalone Verifiable
Sí, contra T2 (se puede mockear la resolución de Usuario en cada router).
