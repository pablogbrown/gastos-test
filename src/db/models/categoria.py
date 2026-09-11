import uuid

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint

from src.db.base import Base
from src.db.types import GUID

# Categorías predefinidas sembradas para toda casa (REQ-001, REQ-002). El
# catálogo real de una casa vive en la tabla `categorias`; esta lista es
# solo el punto de partida sugerido por el documento fuente — el
# Administrador puede agregar más categorías vía `crear_categoria`.
CATEGORIAS_PREDEFINIDAS = [
    "Supermercado",
    "Servicios",
    "Alquiler",
    "Limpieza",
    "Mantenimiento",
    "Mascotas",
    "Comida",
    "Otros",
]


class Categoria(Base):
    """Categoría de gasto administrable por casa (REQ-002)."""

    __tablename__ = "categorias"
    __table_args__ = (
        UniqueConstraint("casa_id", "nombre", name="uq_categoria_casa_nombre"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    nombre = Column(String, nullable=False)

    def __repr__(self):  # pragma: no cover - solo para debugging
        return f"<Categoria id={self.id} nombre={self.nombre!r}>"
