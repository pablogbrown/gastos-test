# T3 — API expone confirmación; endpoint de confirmar/rechazar

## Scope
- `src/api/routes/prestamos.py`
- `tests/integration/api/prestamos_confirmacion_routes.test.py` (nuevo)

## Changes
- `PrestamoOut`: agregar `confirmado_prestamista: Optional[bool] = None`,
  `confirmado_deudor: Optional[bool] = None`, `estado_confirmacion: str`
  (Pydantic lee la property del modelo vía `orm_mode`, igual que
  cualquier otro campo).
- Nuevo schema `PrestamoConfirmacionUpdate {confirma: bool}`.
- Nueva ruta `PATCH /casas/{casa_id}/prestamos/{prestamo_id}/confirmacion`
  → `confirmar_prestamo(casa_id, prestamo_id, actor,
  payload.confirma)`, responde `PrestamoOut` (200).
  `PermissionDeniedError` → 403 (TC-004), `ValidationError` → 400
  (TC-007), `NotFoundError` → 404.

## Design Rationale
Ruta propia (no un campo más en el `PATCH` de estado ya existente) —
son dos acciones con modelos de permiso distintos: cambiar
pagado/pendiente es abierto a cualquier miembro activo; confirmar/
rechazar exige ser específicamente una de las dos partes.

## Dependencies
T2 (`confirmar_prestamo`).

## Done When
- [ ] TC-004, TC-005, TC-006, TC-007 pasan a nivel HTTP.

## Interfaces Produced
- `PrestamoConfirmacionUpdate`.

## Interfaces Consumed
- T2: `confirmar_prestamo`, `actualizar_estado_prestamo`.

## Standalone Verifiable
Sí.
