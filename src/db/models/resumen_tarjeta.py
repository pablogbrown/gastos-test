import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String

from src.db.base import Base
from src.db.types import GUID


class ResumenTarjeta(Base):
    """Un resumen de tarjeta importado con éxito — spec `resumen-tarjeta-
    pago`, REQ-001.

    Una fila por importación exitosa (nunca se actualiza salvo por
    `pagar_resumen`, que solo toca `estado`): tarjeta de origen, ciclo
    (`fecha_cierre`/`fecha_vencimiento`), saldos informados por el PDF,
    cantidad de gastos que esa importación generó, y estado
    `"pendiente"`/`"pagado"` (REQ-004). `(tarjeta_id, fecha_cierre)` es la
    clave natural que `resumen_importer_service.importar_resumen` usa
    para rechazar una segunda importación del mismo resumen (REQ-002) —
    sin `UNIQUE` a nivel de esquema, mismo criterio ya establecido para
    invariantes de negocio de este proyecto ([SERV-01],
    `.nybo/memory/domains/services.md`): el chequeo vive en el service
    layer, antes de escribir nada.

    `tarjeta_id` usa `ForeignKey()` real a nivel de modelo — a diferencia
    de `Gasto.resumen_id` (ver docstring de esa columna en
    `src/db/models/gasto.py`), acá es seguro: `tarjetas_credito` ya
    existe desde la migración `0011`, muy anterior a `0019` (la que crea
    esta tabla), así que `Base.metadata` ya la tiene registrada cuando
    esta clase se declara.
    """

    __tablename__ = "resumenes_tarjeta"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    tarjeta_id = Column(GUID(), ForeignKey("tarjetas_credito.id"), nullable=False)
    fecha_cierre = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    saldo_ars = Column(Numeric(12, 2), nullable=True)
    saldo_usd = Column(Numeric(12, 2), nullable=True)
    gastos_creados = Column(Integer, nullable=False, default=0)
    estado = Column(String, nullable=False, default="pendiente")
    importado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<ResumenTarjeta id={self.id} tarjeta_id={self.tarjeta_id} "
            f"fecha_cierre={self.fecha_cierre} estado={self.estado!r}>"
        )
