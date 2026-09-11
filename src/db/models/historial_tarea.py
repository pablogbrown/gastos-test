import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class HistorialTarea(Base):
    """Registro inmutable de cada finalización de una Tarea (REQ-004, REQ-008).

    Tabla append-only: nunca se actualiza ni se borra tras insertarse, ni
    siquiera si la Tarea original cambia de nombre/puntaje después o si el
    miembro que la completó se desactiva más adelante (TC-010).
    """

    __tablename__ = "historial_tarea"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tarea_id = Column(GUID(), ForeignKey("tareas.id"), nullable=False)
    miembro_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
    completada_en = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    puntos_obtenidos = Column(Integer, nullable=False)

    tarea = relationship("Tarea", back_populates="historial")

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<HistorialTarea id={self.id} tarea_id={self.tarea_id} "
            f"miembro_id={self.miembro_id} puntos_obtenidos={self.puntos_obtenidos}>"
        )
