import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, String

from src.db.base import Base
from src.db.types import GUID


class Prestamo(Base):
    """Un préstamo de dinero entre dos miembros de una casa — spec
    `prestamos-entre-miembros`, REQ-001 a REQ-006.

    Entidad propia (mismo criterio que `TarjetaCredito`/`Suscripcion`):
    un préstamo tiene identidad y ciclo de vida propios, completamente
    independientes de `Gasto`/`GastoParticipante`/`balance_service`
    (REQ-005) — nunca extiende ni referencia esas tablas. Es, en sí
    mismo, la relación de deuda completa entre `prestamista_id` (quien
    prestó) y `deudor_id` (quien debe devolver): no hay pagos parciales,
    ni cálculo derivado, ni sugerencia de transferencia — el registro ya
    ES la transferencia.

    `estado` nace `"pendiente"` (default) y se alterna a `"pagado"` y
    viceversa vía `prestamo_service.actualizar_estado_prestamo` — mismo
    patrón que `ESTADOS_VALIDOS`/`estado` de `Gasto`
    (`gastos-estado-pago`), pero con el default invertido (un préstamo
    nace pendiente, un gasto nace pagado).
    """

    __tablename__ = "prestamos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    prestamista_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
    deudor_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
    importe = Column(Numeric(12, 2), nullable=False)
    moneda = Column(String(3), nullable=False, default="ARS")
    descripcion = Column(String, nullable=True)
    fecha = Column(Date, nullable=False)
    estado = Column(String, nullable=False, default="pendiente")
    creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<Prestamo id={self.id} prestamista_id={self.prestamista_id} "
            f"deudor_id={self.deudor_id} importe={self.importe} estado={self.estado!r}>"
        )
