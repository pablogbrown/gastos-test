# T1 — `ItemMantenimiento` + `MaterialMantenimiento`; migración

## Scope
- `src/db/models/mantenimiento.py` (nuevo).
- `src/db/migrations/0017_mantenimiento.py` (nuevo).
- `src/db/migrate.py`.

## Changes
- `ItemMantenimiento` (tabla `items_mantenimiento`):
  ```python
  id = Column(GUID(), primary_key=True, default=uuid.uuid4)
  casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
  nombre = Column(String, nullable=False)
  descripcion = Column(String, nullable=True)
  fecha_estimada = Column(Date, nullable=True)
  recurrente = Column(Boolean, nullable=False, default=False)
  periodicidad = Column(String, nullable=True)
  estado = Column(String, nullable=False, default="pendiente")
  creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

  materiales = relationship(
      "MaterialMantenimiento", back_populates="item", cascade="all, delete-orphan"
  )
  ```
- `MaterialMantenimiento` (tabla `materiales_mantenimiento`):
  ```python
  id = Column(GUID(), primary_key=True, default=uuid.uuid4)
  item_mantenimiento_id = Column(GUID(), ForeignKey("items_mantenimiento.id"), nullable=False)
  nombre = Column(String, nullable=False)
  cantidad = Column(Integer, nullable=False, default=1)
  conseguido = Column(Boolean, nullable=False, default=False)

  item = relationship("ItemMantenimiento", back_populates="materiales")
  ```
- Migración `0017_mantenimiento.py`: crea ambas tablas (mismo patrón que
  `0011_tarjetas_credito.py`/`0014_prestamos.py` — FKs reales a nivel de
  modelo, `casas`/`items_mantenimiento` ya existen en el orden de
  migraciones al momento en que se crea `materiales_mantenimiento`).
- Registrar `0017_mantenimiento` en `_MIGRACIONES` (verificar al
  implementar que sigue siendo el próximo número libre).

## Design Rationale
Ver `00-overview.md` — por qué es una entidad propia y no una extensión
de `Tarea`.

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] Suite completa en verde con los modelos nuevos.
- [ ] Migración corre limpia e idempotente contra Postgres real.

## Interfaces Produced
- `ItemMantenimiento`, `MaterialMantenimiento` (modelos completos).

## Standalone Verifiable
Sí.
