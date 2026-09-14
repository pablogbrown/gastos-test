import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class Usuario(Base):
    """Identidad global de una persona (REQ-001/REQ-002).

    Separado de `Miembro` (rol dentro de una Casa puntual): un mismo
    Usuario puede tener un `Miembro` en más de una Casa (REQ-004), cada
    uno con su propio `Miembro.id`, todos vinculados al mismo
    `Usuario.id` vía `Miembro.usuario_id`.
    """

    __tablename__ = "usuarios"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    nombre = Column(String, nullable=True)
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    miembros = relationship("Miembro", back_populates="usuario")

    def __repr__(self):  # pragma: no cover - solo para debugging
        return f"<Usuario id={self.id} email={self.email!r}>"
