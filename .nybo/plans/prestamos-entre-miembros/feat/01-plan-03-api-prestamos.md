# T3 — Rutas de préstamos

## Scope
- `src/api/routes/prestamos.py` (nuevo).
- `src/api/main.py` — registrar `prestamos_router`.
- `tests/integration/api/prestamos_routes.test.py` (nuevo).

## Changes
- `prestamos.py`: `PrestamoCreate {prestamista_id, deudor_id, importe,
  moneda?, fecha, descripcion?}`, `PrestamoEstadoUpdate {estado}`,
  `PrestamoOut` — mismo patrón que `tarjetas.py` (esquemas Pydantic en
  el propio archivo de ruta).
  - `POST /casas/{id}/prestamos` → `crear_prestamo`. `ValidationError` →
    400, `NotFoundError` → 404.
  - `GET /casas/{id}/prestamos` → `listar_prestamos`.
  - `PATCH /casas/{id}/prestamos/{prestamo_id}` → `actualizar_estado_prestamo`.

## Design Rationale
Router propio — mismo criterio que separó `tarjetas.py`/
`suscripciones.py`/`gastos.py` entre sí.

## Dependencies
T2 (`prestamo_service`).

## Done When
- [ ] TC-001 a TC-005 pasan a nivel HTTP.

## Interfaces Produced
- `PrestamoOut`, `PrestamoCreate`, `PrestamoEstadoUpdate`.

## Interfaces Consumed
- T2: `crear_prestamo`, `listar_prestamos`, `actualizar_estado_prestamo`.

## Standalone Verifiable
Sí.
