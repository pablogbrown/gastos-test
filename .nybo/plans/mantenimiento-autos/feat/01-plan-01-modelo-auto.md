# T1 — `Auto`; `ItemMantenimiento.auto_id`; migración

## Scope
- `src/db/models/auto.py` (nuevo).
- `src/db/models/mantenimiento.py`.
- `src/db/migrations/0018_mantenimiento_autos.py` (nuevo).
- `src/db/migrate.py`.

## Changes
- `Auto` (tabla `autos`):
  ```python
  id = Column(GUID(), primary_key=True, default=uuid.uuid4)
  casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
  marca = Column(String, nullable=False)
  modelo = Column(String, nullable=False)
  patente = Column(String, nullable=True)
  anio = Column(Integer, nullable=True)
  creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
  ```
- `ItemMantenimiento`: agregar `auto_id = Column(GUID(), ForeignKey("autos.id"), nullable=True)`
  — FK real a nivel de modelo (`autos` se crea en la misma migración,
  antes de esta columna, así que ya está en `Base.metadata` — sin el
  problema de `NoReferencedTableError` documentado para otras columnas
  de este proyecto).
- Migración `0018_mantenimiento_autos.py`: crea `autos`, luego `ALTER
  TABLE items_mantenimiento ADD COLUMN IF NOT EXISTS auto_id UUID
  REFERENCES autos(id)`.
- Registrar `0018_mantenimiento_autos` en `_MIGRACIONES` (verificar al
  implementar que sigue siendo el próximo número libre).

## Design Rationale
Una sola migración para ambos cambios de esquema — están estrechamente
acoplados (la columna no tiene sentido sin la tabla) y siempre se
shippean juntos.

## Dependencies
Ninguna — primera tarea. (Depende de que `mantenimiento-casa` ya esté
mergeada para que `items_mantenimiento` exista.)

## Done When
- [ ] Suite completa en verde con los modelos actualizados.
- [ ] Migración corre limpia e idempotente contra Postgres real.

## Interfaces Produced
- `Auto` (modelo completo), `ItemMantenimiento.auto_id`.

## Standalone Verifiable
Sí.
