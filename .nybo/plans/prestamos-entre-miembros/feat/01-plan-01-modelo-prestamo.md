# T1 — Modelo `Prestamo` + migración

## Scope
- `src/db/models/prestamo.py` (nuevo).
- `src/db/migrations/0015_prestamos.py` (nuevo).
- `src/db/migrate.py`.

## Changes
- `Prestamo` (tabla `prestamos`):
  ```python
  id = Column(GUID(), primary_key=True, default=uuid.uuid4)
  casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
  prestamista_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
  deudor_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
  importe = Column(Numeric(12, 2), nullable=False)
  moneda = Column(String(3), nullable=False, default="ARS")
  descripcion = Column(String, nullable=True)
  fecha = Column(Date, nullable=False)
  estado = Column(String, nullable=False, default="pendiente")
  creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
  ```
- Migración `0015_prestamos.py`: crea la tabla completa (mismo patrón
  que `0011_tarjetas_credito.py` — `casas`/`miembros` ya existen en el
  orden de migraciones, FKs a nivel de modelo sin problema).
- Registrar `0015_prestamos` en `_MIGRACIONES` (verificar al implementar
  que sigue siendo el próximo número libre).

## Design Rationale
Entidad propia — mismo criterio que `TarjetaCredito`/`Suscripcion`: un
préstamo tiene identidad y ciclo de vida propios, independientes de
cualquier `Gasto`.

## Dependencies
Ninguna — primera tarea. (No depende de `gastos-sin-reparto` — no toca
`Gasto`/`GastoParticipante` en absoluto.)

## Done When
- [ ] Suite completa en verde con el modelo nuevo.
- [ ] Migración corre limpia e idempotente contra Postgres real.

## Interfaces Produced
- `Prestamo` (modelo completo).

## Standalone Verifiable
Sí.
