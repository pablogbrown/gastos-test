# Task 3 — API Routes: Casas y Miembros

## Scope
- `src/api/routes/casas.py`

## Changes
### API Route
- `POST /casas` → `crear_casa`.
- `POST /casas/{casaId}/miembros` → `agregar_miembro`.
- `PATCH /casas/{casaId}/miembros/{miembroId}` → `desactivar_miembro` (body `{activo: false}`).
- `GET /casas/{casaId}/miembros` → listado de miembros (activos e inactivos, con flag).
- Cada ruta aplica el guard de permisos de T2 antes de invocar el servicio.

## Design Rationale
Las rutas son adaptadores delgados sobre los servicios de T2 (sin lógica de negocio propia), manteniendo la regla de una sola responsabilidad por capa.

## Dependencies
T2 (servicios de casa/miembro/permisos).

## Done When
- [ ] TC-006, TC-007, TC-008 verificados a nivel de contrato HTTP (status codes 201/403/400 según corresponda).
- [ ] Rutas registradas en el router principal.
- [ ] Build succeeds.

## Interfaces Produced
- `{name: "casas_router", signature: "APIRouter", kind: "export"}`

## Standalone Verifiable
Sí, contra los servicios de T2 (se puede mockear la capa HTTP).
