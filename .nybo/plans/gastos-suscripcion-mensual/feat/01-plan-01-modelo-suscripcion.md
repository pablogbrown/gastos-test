# T1 — Modelo `Suscripcion` + FK en `Gasto`

## Scope
- `src/db/models/suscripcion.py` (nuevo).
- `src/db/models/gasto.py` — nueva columna `suscripcion_id`.
- `src/db/migrations/0009_suscripciones.py` (nuevo).
- `src/db/migrate.py` — agregar `0009` a `_MIGRACIONES`.

## Changes
**Data Layer**
- Nuevo modelo `Suscripcion` (tabla `suscripciones`):
  ```python
  class Suscripcion(Base):
      __tablename__ = "suscripciones"

      id = Column(GUID(), primary_key=True, default=uuid.uuid4)
      casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
      descripcion = Column(String, nullable=False)
      importe = Column(Numeric(12, 2), nullable=False)
      categoria_id = Column(GUID(), ForeignKey("categorias.id"), nullable=False)
      pagado_por = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
      activa = Column(Boolean, default=True, nullable=False)
      ultimo_mes_generado = Column(String, nullable=True)
      creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
  ```
- `Gasto`: agregar `suscripcion_id = Column(GUID(), ForeignKey("suscripciones.id"), nullable=True)`.
- Migración `0009_suscripciones.py`: crea la tabla `suscripciones`
  (`TABLES = [Suscripcion.__table__]`, importando `Casa`/`Categoria`/
  `Miembro` para registrar sus tablas referenciadas — mismo patrón que
  `0004_historial_actividad.py`) y agrega `suscripcion_id` a `gastos`
  vía `ALTER TABLE gastos ADD COLUMN IF NOT EXISTS suscripcion_id UUID
  REFERENCES suscripciones(id)`.

## Design Rationale
Tabla propia (no columnas sueltas en `Gasto`) porque, a diferencia de
una cuota, una suscripción tiene identidad y estado propios
(activa/inactiva) que sobreviven independientemente de cualquier gasto
puntual que haya generado — necesita poder listarse y cancelarse aunque
todavía no haya generado ningún gasto este mes.

## Dependencies
Ninguna — primera tarea.

## Done When
- [x] Suite completa en verde con el modelo nuevo.
- [x] Migración corre limpia e idempotente contra Postgres real (base
      temporal, nunca `DATABASE_URL` directo).

## Interfaces Produced
- `Suscripcion` — modelo nuevo, exportado desde `src/db/models/suscripcion.py`.
- `Gasto.suscripcion_id` — `Optional[UUID]`.

## Standalone Verifiable
Sí.
