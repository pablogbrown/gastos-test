import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from src.db.base import Base
from src.db.types import GUID


class Auto(Base):
    """Un auto de la casa (spec `mantenimiento-autos`, REQ-001) — entidad
    propia de la casa, no de un miembro específico (mismo criterio que
    `TarjetaCredito`: aunque un miembro sea quien más lo usa, no hay
    "dueño" a nivel de datos — cualquier miembro activo puede registrarlo
    y verlo).

    Sin kilometraje ni intervalos en km (decisión explícita del usuario,
    ver `00-overview.md`'s Tradeoffs) — la periodicidad de un ítem de
    mantenimiento asociado a un auto es por fecha, igual que el resto de
    la app.
    """

    __tablename__ = "autos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    marca = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    patente = Column(String, nullable=True)
    anio = Column(Integer, nullable=True)
    creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):  # pragma: no cover - solo para debugging
        return f"<Auto id={self.id} marca={self.marca!r} modelo={self.modelo!r}>"
