# Task 3 — API Routes: Dashboard y Actividad

## Scope
- `src/api/routes/dashboard.py`

## Changes
### API Route
- `GET /casas/{casaId}/inicio` → `armar_dashboard`.
- `GET /casas/{casaId}/actividad` → `obtener_actividad`.

## Design Rationale
Rutas de solo lectura, sin necesidad de guard de rol especial más allá de membresía activa (cualquier miembro puede consultar, REQ-003).

## Dependencies
T2.

## Done When
- [ ] Contratos HTTP verificados (200 con estructura esperada, incluso con datos vacíos).
- [ ] Build succeeds.

## Interfaces Produced
- `{name: "dashboard_router", signature: "APIRouter", kind: "export"}`

## Standalone Verifiable
Sí.
