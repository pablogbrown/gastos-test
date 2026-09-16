# T2 — `GET .../gastos?mes=`

## Scope
- `src/api/routes/gastos.py`
- `tests/integration/api/gastos_mes_routes.test.py` (nuevo)

## Changes
- `listar_gastos_endpoint(casa_id, mes: Optional[str] = None, actor=...)`:
  agrega el query param `mes` y lo pasa a `listar_gastos`.
  `ValidationError` (formato inválido) → 400.

## Design Rationale
Mismo patrón que `GET /casas/{id}/balance?mes=` ya existente.

## Dependencies
T1 (`listar_gastos` acepta `mes`).

## Done When
- [ ] TC-003 pasa.

## Interfaces Produced
Ninguna (parámetro nuevo en un endpoint existente).

## Interfaces Consumed
- T1: `listar_gastos`.

## Standalone Verifiable
Sí.
