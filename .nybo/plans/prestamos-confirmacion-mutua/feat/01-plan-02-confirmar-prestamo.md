# T2 — Auto-confirmación al crear; `confirmar_prestamo`; guard en el cambio de estado

## Scope
- `src/services/prestamo_service.py`
- `tests/integration/services/prestamo_confirmacion.test.py` (nuevo)

## Changes
- `crear_prestamo`: después de validar `prestamista_id`/`deudor_id`,
  fijar:
  ```python
  confirmado_prestamista = True if actor == prestamista_id else None
  confirmado_deudor = True if actor == deudor_id else None
  ```
  (TC-001/TC-002/TC-003 — si `actor` no es ninguna de las dos partes,
  ambos quedan `None`).
- `confirmar_prestamo(casa_id, prestamo_id, actor, confirma: bool) -> Prestamo`
  (nueva):
  - Busca el préstamo en la casa (`NotFoundError` si no existe).
  - `raise ValidationError` si `prestamo.estado_confirmacion !=
    "pendiente_confirmacion"` (TC-005/TC-006 solo aplican mientras está
    pendiente — un préstamo ya confirmado o rechazado no vuelve a
    aceptar esta acción).
  - Si `actor == prestamo.prestamista_id`: fija
    `confirmado_prestamista = confirma`.
  - Elif `actor == prestamo.deudor_id`: fija `confirmado_deudor =
    confirma`.
  - Else: `raise PermissionDeniedError` (TC-004) — ni
    `requiere_membresia_activa` alcanza acá: tiene que ser
    específicamente una de las dos partes de ESE préstamo.
- `actualizar_estado_prestamo`: agregar, antes de aplicar el cambio,
  `if prestamo.estado_confirmacion != "confirmado": raise
  ValidationError(...)` (TC-007).

## Design Rationale
`confirmar_prestamo` no reutiliza `requiere_membresia_activa` como único
guard — ese guard responde "¿sos miembro activo de la casa?", no "¿sos
una de las dos partes de este préstamo específico?" — son dos preguntas
distintas y esta función necesita la segunda.

## Dependencies
T1 (`confirmado_prestamista`/`confirmado_deudor`/`estado_confirmacion`).

## Done When
- [ ] TC-001 a TC-007 pasan.

## Interfaces Produced
- `confirmar_prestamo(casa_id, prestamo_id, actor, confirma) -> Prestamo`.

## Standalone Verifiable
Sí.
