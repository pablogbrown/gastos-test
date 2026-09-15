import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String

from src.db.base import Base
from src.db.types import GUID


class Suscripcion(Base):
    """Un gasto recurrente mensual (ej. Netflix, gimnasio) — spec
    `gastos-suscripcion-mensual`, REQ-001.

    Entidad propia (no columnas sueltas en `Gasto`): a diferencia de una
    cuota (`gastos-en-cuotas`, con un fin definido), una suscripción tiene
    identidad y estado propios (`activa`) que sobreviven
    independientemente de cualquier `Gasto` puntual que haya generado —
    necesita poder listarse y cancelarse aunque todavía no haya generado
    ningún gasto este mes.

    `ultimo_mes_generado` (`YYYY-MM`, `None` hasta la primera generación)
    es lo que `suscripcion_service.generar_gastos_pendientes` usa para
    decidir si ya generó el gasto del mes actual — nunca reconstruye
    retroactivamente meses pasados (REQ-002).

    `moneda` (spec `gastos-multi-moneda`): `"ARS"` (default) o `"USD"` —
    fija desde la creación (no hay endpoint de edición hoy); cada gasto
    generado mensualmente hereda esta misma moneda.
    """

    __tablename__ = "suscripciones"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    descripcion = Column(String, nullable=False)
    importe = Column(Numeric(12, 2), nullable=False)
    categoria_id = Column(GUID(), ForeignKey("categorias.id"), nullable=False)
    pagado_por = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
    activa = Column(Boolean, default=True, nullable=False)
    ultimo_mes_generado = Column(String, nullable=True)
    creado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    moneda = Column(String(3), nullable=False, default="ARS")

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<Suscripcion id={self.id} descripcion={self.descripcion!r} "
            f"activa={self.activa}>"
        )
