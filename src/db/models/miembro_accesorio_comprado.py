from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey

from src.db.base import Base
from src.db.types import GUID


class MiembroAccesorioComprado(Base):
    """Inventario de accesorios comprados por un miembro (spec
    `tienda-accesorios`, REQ-002) — clave primaria compuesta
    `(miembro_id, accesorio_id)`: a lo sumo una fila por par, lo que hace
    "no se puede comprar el mismo accesorio dos veces" una garantía de
    esquema además de la validación en `tienda_service.comprar_accesorio`
    (TC-005) — mismo criterio que `MiembroAccesorioEquipado` (T3) usa
    `(miembro_id, slot)` para su propio invariante.

    `miembro_id`/`accesorio_id` llevan `ForeignKey()` real: `miembros`
    (migración `0001`) y `accesorios_avatar` (migración `0024`) son ambas
    anteriores a esta `0025`, así que `create_all` resuelve esos
    `ForeignKey()` sin problema ([DBG-02]/[DBG-03] no aplica, mismo
    criterio que `MiembroAvatarSeleccionado`).
    """

    __tablename__ = "miembro_accesorio_comprado"

    miembro_id = Column(GUID(), ForeignKey("miembros.id"), primary_key=True)
    accesorio_id = Column(GUID(), ForeignKey("accesorios_avatar.id"), primary_key=True)
    comprado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<MiembroAccesorioComprado miembro_id={self.miembro_id} "
            f"accesorio_id={self.accesorio_id}>"
        )
