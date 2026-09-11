import enum
import uuid

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class EstadoTareaEnum(str, enum.Enum):
    """Ciclo de vida de una Tarea (REQ-002)."""

    PENDIENTE = "pendiente"
    EN_CURSO = "en_curso"
    COMPLETADA = "completada"


class Tarea(Base):
    """Una tarea doméstica de una Casa, con puntos y responsable opcional
    (REQ-001, REQ-003). Puede ser recurrente: al completarse, el servicio de
    tareas genera una nueva instancia según `frecuencia` (REQ-007).
    """

    __tablename__ = "tareas"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    puntos = Column(Integer, nullable=False)
    responsable_id = Column(GUID(), ForeignKey("miembros.id"), nullable=True)
    fecha_prevista = Column(Date, nullable=True)
    estado = Column(Enum(EstadoTareaEnum), nullable=False, default=EstadoTareaEnum.PENDIENTE)
    recurrente = Column(Boolean, nullable=False, default=False)
    frecuencia = Column(String, nullable=True)

    historial = relationship(
        "HistorialTarea", back_populates="tarea", cascade="all, delete-orphan"
    )

    def __repr__(self):  # pragma: no cover - solo para debugging
        return f"<Tarea id={self.id} nombre={self.nombre!r} estado={self.estado}>"
