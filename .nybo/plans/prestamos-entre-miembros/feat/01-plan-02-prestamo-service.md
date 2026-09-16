# T2 — `prestamo_service` (alta/listado/estado)

## Scope
- `src/services/prestamo_service.py` (nuevo).
- `tests/integration/services/prestamo_service.test.py` (nuevo).

## Changes
- `ESTADOS_PRESTAMO_VALIDOS = {"pendiente", "pagado"}`.
- `crear_prestamo(casa_id, prestamista_id, deudor_id, importe, moneda, fecha, actor, descripcion=None) -> Prestamo`:
  - Valida `prestamista_id != deudor_id` (TC-002); ambos deben ser
    miembros existentes de la casa (`NotFoundError` si no).
  - Valida `importe > 0`, `moneda` contra
    `gasto_service.MONEDAS_VALIDAS` (import directo, mismo criterio que
    `suscripcion_service.py`) (TC-003).
  - Requiere que `actor` sea miembro activo de la casa
    (`requiere_membresia_activa`, mismo guard que `gasto_service`).
  - Persiste con `estado="pendiente"` (TC-001).
- `listar_prestamos(casa_id) -> List[Prestamo]`: ordenado por `fecha`
  descendente (TC-005).
- `actualizar_estado_prestamo(casa_id, prestamo_id, estado, actor) -> Prestamo`:
  valida `estado` contra `ESTADOS_PRESTAMO_VALIDOS`, actualiza y
  devuelve (TC-004). Mismo nivel de permiso que `crear_prestamo` (sin
  `_validar_actor_admin`).

## Design Rationale
Ver `00-overview.md` — por qué `prestamista_id`/`deudor_id` reutilizan
`gasto_service.MONEDAS_VALIDAS` en vez de duplicarla (a diferencia de
otras utilidades pequeñas sí duplicadas en el proyecto): esta constante
en particular ya se comparte por import directo entre `gasto_service.py`
y `suscripcion_service.py`, mismo criterio acá.

## Dependencies
T1 (`Prestamo`).

## Done When
- [ ] TC-001 a TC-006 pasan (TC-006 confirma que `balance_service.calcular_balance` no cambia tras crear/actualizar un préstamo).

## Interfaces Produced
- `crear_prestamo`, `listar_prestamos`, `actualizar_estado_prestamo`.

## Standalone Verifiable
Sí.
