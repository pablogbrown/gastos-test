import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String

from src.db.base import Base
from src.db.types import GUID


class TipoActividadEnum(str, enum.Enum):
    """Tipos de evento reconocidos en el historial de actividad (REQ-002)."""

    GASTO_REGISTRADO = "gasto_registrado"
    TAREA_CREADA = "tarea_creada"
    TAREA_COMPLETADA = "tarea_completada"
    PUNTOS_OBTENIDOS = "puntos_obtenidos"
    MIEMBRO_AGREGADO = "miembro_agregado"


class HistorialActividad(Base):
    """Event log append-only de las acciones relevantes de una Casa
    (REQ-002, REQ-003).

    Una tabla genérica de eventos (en vez de una por tipo de acción)
    permite listar el historial completo con una sola query ordenada por
    fecha, sin joins múltiples (ver Design Rationale de T1 en
    `01-plan-01-data-layer.md`). Al igual que `HistorialTarea`, nunca se
    actualiza ni se borra tras insertarse.
    """

    __tablename__ = "historial_actividad"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    tipo = Column(Enum(TipoActividadEnum), nullable=False)
    # Nullable: un evento futuro podría no tener un miembro puntual
    # asociado (p. ej. una acción a nivel de la casa en su conjunto).
    miembro_id = Column(GUID(), ForeignKey("miembros.id"), nullable=True)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    descripcion = Column(String, nullable=False)

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<HistorialActividad id={self.id} tipo={self.tipo} "
            f"descripcion={self.descripcion!r}>"
        )
