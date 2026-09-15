# T1 — Modelo `TarjetaCredito` + migración

## Scope
- `src/db/models/tarjeta_credito.py` (nuevo).
- `src/db/migrations/0011_tarjetas_credito.py` (nuevo).
- `src/db/migrate.py` — agregar `0011` a `_MIGRACIONES`.

## Changes
**Data Layer**
- `TarjetaCredito` (tabla `tarjetas_credito`):
  ```python
  id = Column(GUID(), primary_key=True, default=uuid.uuid4)
  casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
  miembro_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
  banco = Column(String, nullable=False)
  nombre = Column(String, nullable=False)
  ultimos_digitos = Column(String(4), nullable=False)
  fecha_cierre_actual = Column(Date, nullable=False)
  fecha_vencimiento_actual = Column(Date, nullable=False)
  saldo_actual_ars = Column(Numeric(12, 2), nullable=True)
  saldo_actual_usd = Column(Numeric(12, 2), nullable=True)
  activa = Column(Boolean, default=True, nullable=False)
  creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
  ```
- Migración `0011_tarjetas_credito.py`: crea la tabla completa (mismo
  patrón que `0009_suscripciones.py`) — `casas`/`miembros` ya existen en
  el orden de migraciones, así que las FKs se declaran a nivel de
  modelo sin el problema de `NoReferencedTableError` documentado para
  `Gasto.suscripcion_id`.
- Registrar `0011_tarjetas_credito` en `_MIGRACIONES`, después de `0010`
  (o el próximo número realmente libre al momento de implementar).

## Design Rationale
Entidad propia (no columnas en `Miembro`/`Casa`): una tarjeta tiene
identidad, dueño y ciclo de vida propios, igual que `Suscripcion`.

## Dependencies
Ninguna — primera tarea. (No depende de `gastos-multi-moneda`: esta
entidad no toca `Gasto` en absoluto todavía.)

## Done When
- [ ] Suite completa en verde con el modelo nuevo.
- [ ] Migración corre limpia e idempotente contra Postgres real.

## Interfaces Produced
- `TarjetaCredito` (modelo completo, ver Changes).

## Standalone Verifiable
Sí.
