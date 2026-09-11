# Task 3 — API Routes: Gastos y Balance

## Scope
- `src/api/routes/gastos.py`

## Changes
### API Route
- `POST /casas/{casaId}/categorias` → `crear_categoria`.
- `POST /casas/{casaId}/gastos` → `registrar_gasto`.
- `GET /casas/{casaId}/gastos` → historial ordenado por fecha descendente (TC-010, incluye gastos de miembros desactivados).
- `GET /casas/{casaId}/balance` → `calcular_balance` + `sugerir_transferencias`.

## Design Rationale
Rutas delgadas sobre T2, consistente con el patrón ya usado en `casas-miembros`.

## Dependencies
T2.

## Done When
- [ ] Contratos HTTP verificados (400 sin categoría, 403 sin rol admin al crear categoría).
- [ ] Build succeeds.

## Interfaces Produced
- `{name: "gastos_router", signature: "APIRouter", kind: "export"}`

## Standalone Verifiable
Sí.
