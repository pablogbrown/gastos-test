import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class ItemMantenimiento(Base):
    """Un ítem de mantenimiento de la casa (spec `mantenimiento-casa`,
    REQ-001/REQ-002) — entidad propia, nunca una extensión de `Tarea`:
    "Tareas" es gamificación con puntos/ranking entre miembros, esto es
    trabajo de mantenimiento del hogar (a veces caro, a veces con compras
    de materiales previas), sin ninguno de esos dos conceptos.

    Recurrente exige `periodicidad` Y `fecha_estimada` al crearse (mismo
    criterio recién corregido en `tarea_service.crear_tarea` — sin una
    fecha de anclaje no hay forma de impedir que se complete más seguido
    que su periodicidad). Al completar una instancia recurrente,
    `mantenimiento_service.completar_item` genera una nueva instancia
    pendiente con la fecha siguiente.

    `auto_id` (spec `mantenimiento-autos`, REQ-002/REQ-003): `NULL` es
    mantenimiento de la casa (comportamiento sin cambios); poblado
    vincula el ítem a un `Auto` puntual. Declarado como `Column` plano,
    SIN `ForeignKey()` a nivel de modelo — mismo criterio ya documentado
    en `[DBG-02]`/`[DBG-03]` (`.nybo/memory/domains/db.md`): la migración
    que CREA esta tabla (`0017_mantenimiento.py`) corre ANTES que
    `0018_mantenimiento_autos.py` (que crea `autos`), así que un
    `ForeignKey("autos.id")` acá rompería `0017.upgrade()` con
    `relation "autos" does not exist` en cualquier base creada desde
    cero. El FK real se agrega vía SQL crudo en `0018`, después de crear
    `autos` en esa misma migración.
    """

    __tablename__ = "items_mantenimiento"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    fecha_estimada = Column(Date, nullable=True)
    recurrente = Column(Boolean, nullable=False, default=False)
    periodicidad = Column(String, nullable=True)
    estado = Column(String, nullable=False, default="pendiente")
    creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    auto_id = Column(GUID(), nullable=True)

    materiales = relationship(
        "MaterialMantenimiento", back_populates="item", cascade="all, delete-orphan"
    )

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<ItemMantenimiento id={self.id} nombre={self.nombre!r} estado={self.estado!r}>"
        )


class MaterialMantenimiento(Base):
    """Un material necesario para un `ItemMantenimiento` (REQ-003):
    nombre, cantidad y si ya fue conseguido — sin tracking de costo
    (decisión explícita del usuario, ver `00-overview.md`)."""

    __tablename__ = "materiales_mantenimiento"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    item_mantenimiento_id = Column(GUID(), ForeignKey("items_mantenimiento.id"), nullable=False)
    nombre = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    conseguido = Column(Boolean, nullable=False, default=False)

    item = relationship("ItemMantenimiento", back_populates="materiales")

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<MaterialMantenimiento id={self.id} nombre={self.nombre!r} "
            f"conseguido={self.conseguido}>"
        )
