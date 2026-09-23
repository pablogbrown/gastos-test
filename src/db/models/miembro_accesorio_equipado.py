from sqlalchemy import Column, ForeignKey, String

from src.db.base import Base
from src.db.types import GUID


class MiembroAccesorioEquipado(Base):
    """Accesorio actualmente equipado por slot, por miembro (spec
    `tienda-accesorios`, REQ-003) — clave primaria compuesta
    `(miembro_id, slot)`: como máximo un accesorio activo por slot por
    miembro es una garantía de esquema, no solo del service layer
    (`tienda_service.equipar_accesorio` hace upsert sobre esta clave, ver
    Design Rationale de T3) — más fuerte que un `SERV-01`-style check
    puramente en el service layer para este caso puntual, porque la
    violación sería estructuralmente imposible.

    `accesorio_id` lleva `ForeignKey()` real: `accesorios_avatar`
    (migración `0024`) es anterior a esta `0026`, así que `create_all`
    resuelve el `ForeignKey()` sin problema ([DBG-02]/[DBG-03] no
    aplica).
    """

    __tablename__ = "miembro_accesorio_equipado"

    miembro_id = Column(GUID(), ForeignKey("miembros.id"), primary_key=True)
    slot = Column(String, primary_key=True)
    accesorio_id = Column(GUID(), ForeignKey("accesorios_avatar.id"), nullable=False)

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<MiembroAccesorioEquipado miembro_id={self.miembro_id} "
            f"slot={self.slot!r} accesorio_id={self.accesorio_id}>"
        )
