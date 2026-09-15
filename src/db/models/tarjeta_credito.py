import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Numeric, String

from src.db.base import Base
from src.db.types import GUID


class TarjetaCredito(Base):
    """Una tarjeta de crédito registrada por un miembro de la casa —
    spec `tarjetas-credito`, REQ-001.

    Entidad propia (no columnas en `Miembro`/`Casa`): una tarjeta tiene
    identidad, dueño (`miembro_id`) y ciclo de vida propios (alta, edición
    de cierre/vencimiento/saldo, baja), igual que `Suscripcion` — no
    depende de que exista ningún `Gasto` todavía. Es además la base para
    la spec dependiente `importar-resumen-tarjeta`: cada resumen
    importado pertenecerá a una tarjeta ya registrada acá.

    `fecha_cierre_actual`/`fecha_vencimiento_actual` reflejan siempre el
    resumen más reciente conocido (actualización manual en esta spec,
    REQ-002) — no hay historial de resúmenes anteriores. `saldo_actual_
    ars`/`saldo_actual_usd` son `nullable` porque una tarjeta recién
    creada todavía no tiene ningún resumen cargado (REQ-001).

    `activa` (soft-delete, REQ-003): desactivar preserva el registro para
    no perder historial, mismo criterio que desactivar un `Miembro`.
    """

    __tablename__ = "tarjetas_credito"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    miembro_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
    banco = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    ultimos_digitos = Column(String(4), nullable=False)
    fecha_cierre_actual = Column(Date, nullable=False)
    fecha_vencimiento_actual = Column(Date, nullable=False)
    saldo_actual_ars = Column(Numeric(12, 2), nullable=True)
    saldo_actual_usd = Column(Numeric(12, 2), nullable=True)
    activa = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<TarjetaCredito id={self.id} nombre={self.nombre!r} "
            f"banco={self.banco!r} activa={self.activa}>"
        )
