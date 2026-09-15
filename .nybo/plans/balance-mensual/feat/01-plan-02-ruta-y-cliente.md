# T2 — Ruta y cliente HTTP exponen `mes`

## Scope
- `src/api/routes/gastos.py` — `obtener_balance_endpoint`.
- `src/frontend/api/gastosClient.ts` — `obtenerBalance`.
- `tests/integration/api/gastos_routes.test.py` — TC-003 (a nivel HTTP).

## Changes
**API Route**
- `obtener_balance_endpoint(casa_id: UUID, mes: Optional[str] = None, actor: UUID = Depends(...))`
  (query param `mes`, FastAPI lo infiere de un parámetro no-path/no-body
  con default). Pasar `mes` a `calcular_balance`. Capturar
  `ValidationError` → 400 (mismo patrón que el resto de los handlers de
  este router).

**UI (cliente HTTP)**
- `obtenerBalance(casaId: string, mes?: string): Promise<BalanceResponse>`
  — agrega `?mes=${mes}` a la URL solo si `mes` está presente.

## Design Rationale
Pass-through simple en ambas capas — ninguna decide nada, solo
transportan el parámetro que T1 ya sabe interpretar.

## Dependencies
T1 — necesita que `calcular_balance` acepte `mes`.

## Done When
- [ ] TC-003 (400 con mes inválido) pasa a nivel HTTP.
- [ ] `pytest tests/` y `npm run build` siguen en verde.

## Interfaces Produced
Ninguna nueva — extiende una ruta y una función de cliente ya existentes.

## Standalone Verifiable
Sí.
