# T1 — `Prestamo` guarda confirmación por rol; migración

## Scope
- `src/db/models/prestamo.py`
- `src/db/migrations/0016_prestamo_confirmacion.py` (nuevo)
- `src/db/migrate.py`

## Changes
- `Prestamo`: agregar
  ```python
  confirmado_prestamista = Column(Boolean, nullable=True)
  confirmado_deudor = Column(Boolean, nullable=True)
  ```
  y una property Python (no columna):
  ```python
  @property
  def estado_confirmacion(self) -> str:
      if self.confirmado_prestamista is False or self.confirmado_deudor is False:
          return "rechazado"
      if self.confirmado_prestamista is True and self.confirmado_deudor is True:
          return "confirmado"
      return "pendiente_confirmacion"
  ```
- Migración `0016_prestamo_confirmacion.py`: `ALTER TABLE prestamos ADD
  COLUMN IF NOT EXISTS confirmado_prestamista BOOLEAN`, ídem
  `confirmado_deudor` — ambas sin `DEFAULT` (nullable, `NULL` implícito),
  mismo patrón aditivo que `0010`/`0011`/`0013`.
- Registrar `0016_prestamo_confirmacion` en `_MIGRACIONES` (verificar al
  implementar que sigue siendo el próximo número libre).

## Design Rationale
`estado_confirmacion` es una property, no una columna — se deriva
siempre de los dos booleanos, nunca se persiste por separado (ver
Tradeoffs de `00-overview.md`).

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] Suite completa en verde con el modelo actualizado.
- [ ] Migración corre limpia e idempotente contra Postgres real.
- [ ] Un `Prestamo` recién creado (sin las nuevas columnas explícitas) tiene `estado_confirmacion == "pendiente_confirmacion"`.

## Interfaces Produced
- `Prestamo.confirmado_prestamista`, `Prestamo.confirmado_deudor`, `Prestamo.estado_confirmacion` (property).

## Standalone Verifiable
Sí.
