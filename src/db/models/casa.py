import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class Casa(Base):
    """Una casa/hogar que agrupa miembros, gastos y tareas."""

    __tablename__ = "casas"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, nullable=False)
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    miembros = relationship(
        "Miembro", back_populates="casa", cascade="all, delete-orphan"
    )

    def __repr__(self):  # pragma: no cover - solo para debugging
        return f"<Casa id={self.id} nombre={self.nombre!r}>"
