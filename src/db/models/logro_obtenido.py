import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class LogroObtenido(Base):
    """Registro de un logro desbloqueado por un miembro (spec
    `gamificacion-puntos`, REQ-004).

    `logro_id` es un `String` PLANO, no una FK a una tabla de catálogo —
    el catálogo de logros (`logro_service.LOGROS_CATALOGO`) es fijo en
    código, no una entidad editable (ver Tradeoffs, `00-overview.md`).

    `casa_id`/`miembro_id` sí llevan `ForeignKey()` real a nivel de
    modelo: `casas`/`miembros` se crearon en la migración `0001`, muy
    anterior a la `0020` que crea esta tabla — mismo caso seguro que
    `ResumenTarjeta.tarjeta_id`, no el caso `Gasto.resumen_id` ([DBG-02]).
    """

    __tablename__ = "logros_obtenidos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    miembro_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
    logro_id = Column(String, nullable=False)
    obtenido_en = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    casa = relationship("Casa")
    miembro = relationship("Miembro")

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<LogroObtenido id={self.id} miembro_id={self.miembro_id} "
            f"logro_id={self.logro_id!r}>"
        )
