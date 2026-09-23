import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class CreditoTransaccion(Base):
    """Ledger append-only de créditos (spec `avatares-economia`, REQ-001).

    Un crédito es una moneda de personalización separada de los puntos de
    ranking, ganada en paralelo al completar una tarea. Igual que
    `HistorialTarea`/el ranking de puntos, el saldo de un miembro se
    DERIVA sumando sus filas acá (`avatar_service.obtener_balance_creditos`)
    — nunca se guarda un contador cacheado en `Miembro` (mismo criterio ya
    establecido para `ranking_service.calcular_ranking`).

    `casa_id`/`miembro_id` son `ForeignKey` directo: ambas tablas
    (`casas`, `miembros`) ya existen desde la migración `0001`, muy
    anterior a la migración `0021` que crea esta tabla, así que no hay
    riesgo de FK-ordering ([DBG-02]/[DBG-03], `.nybo/memory/domains/db.md`).
    """

    __tablename__ = "credito_transacciones"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    miembro_id = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String, nullable=False)
    creada_en = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    casa = relationship("Casa")
    miembro = relationship("Miembro")

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<CreditoTransaccion id={self.id} miembro_id={self.miembro_id} "
            f"cantidad={self.cantidad} motivo={self.motivo!r}>"
        )
