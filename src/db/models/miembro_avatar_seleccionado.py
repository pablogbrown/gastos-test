from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey

from src.db.base import Base
from src.db.types import GUID


class MiembroAvatarSeleccionado(Base):
    """Avatar actualmente seleccionado por un miembro (spec
    `avatares-economia`, REQ-004) — a lo sumo una fila por miembro
    (`miembro_id` es PK, no solo FK), reemplazada in-place cuando el
    miembro cambia de raza. Sin fila para un miembro: no tiene avatar
    seleccionado (`avatar_service.obtener_avatar_seleccionado` devuelve
    `None`) — nunca se autoasigna una raza por defecto (REQ-004).

    `avatar_personaje_id` lleva `ForeignKey()` real: `avatar_personajes`
    se crea en la migración `0022`, anterior a esta `0023`
    ([DBG-02]/[DBG-03] no aplica, mismo criterio que `CreditoTransaccion`).
    """

    __tablename__ = "miembro_avatar_seleccionado"

    miembro_id = Column(GUID(), ForeignKey("miembros.id"), primary_key=True)
    avatar_personaje_id = Column(GUID(), ForeignKey("avatar_personajes.id"), nullable=False)
    actualizado_en = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<MiembroAvatarSeleccionado miembro_id={self.miembro_id} "
            f"avatar_personaje_id={self.avatar_personaje_id}>"
        )
