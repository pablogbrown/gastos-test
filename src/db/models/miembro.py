import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class RolEnum(str, enum.Enum):
    """Roles reconocidos dentro de una casa (REQ-004)."""

    ADMIN = "admin"
    MEMBER = "member"


class Miembro(Base):
    """Una persona perteneciente a una Casa, con un rol y estado activo.

    `id` funciona como identidad de usuario dentro de esa casa: es el
    valor que otras specs (gastos, tareas-puntos) usan como `usuario_id`
    al llamar a `requiere_membresia_activa`. Una misma persona puede
    pertenecer a varias casas (REQ-006) con un `Miembro.id` distinto en
    cada una.
    """

    __tablename__ = "miembros"
    __table_args__ = (
        UniqueConstraint("casa_id", "identificacion", name="uq_miembro_casa_identificacion"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    nombre = Column(String, nullable=False)
    identificacion = Column(String, nullable=False)
    rol = Column(Enum(RolEnum), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    casa = relationship("Casa", back_populates="miembros")

    def __repr__(self):  # pragma: no cover - solo para debugging
        return f"<Miembro id={self.id} nombre={self.nombre!r} rol={self.rol}>"
