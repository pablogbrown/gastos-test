import uuid

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.types import GUID


class Gasto(Base):
    """Un gasto registrado en una casa (REQ-001).

    `pagado_por` referencia al Miembro que efectivamente pagó (puede ser
    distinto de quien realiza la operación de registro). `categoria_id`
    es obligatorio (REQ-001/TC-002): no existe un gasto sin categoría.

    `cuota_grupo_id`/`cuota_numero`/`cuota_total` (spec `gastos-en-
    cuotas`): `NULL` para un gasto normal (sin cuotas); pobladas juntas
    cuando este `Gasto` es una de las N cuotas generadas al registrar un
    gasto con `cuotas >= 2` — `cuota_grupo_id` comparte el mismo valor
    entre las N filas de una misma compra, `cuota_numero` va de 1 a
    `cuota_total`.

    `suscripcion_id` (spec `gastos-suscripcion-mensual`): `NULL` para un
    gasto normal o en cuotas; poblada cuando este `Gasto` fue generado
    (al crear la suscripción, o automáticamente al listar gastos) por una
    `Suscripcion` — puramente de etiquetado, independiente de `cuotas`
    (un gasto generado por una suscripción nunca tiene `cuotas`, y
    viceversa).

    `moneda` (spec `gastos-multi-moneda`): `"ARS"` (default) o `"USD"` —
    sin conversión entre monedas en ningún lado del sistema. Todas las
    cuotas de una misma compra comparten la misma `moneda`
    (`_crear_gastos_en_cuotas`, `gasto_service.py`).
    """

    __tablename__ = "gastos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
    descripcion = Column(String, nullable=False)
    importe = Column(Numeric(12, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    pagado_por = Column(GUID(), ForeignKey("miembros.id"), nullable=False)
    categoria_id = Column(GUID(), ForeignKey("categorias.id"), nullable=False)
    cuota_grupo_id = Column(GUID(), nullable=True)
    cuota_numero = Column(Integer, nullable=True)
    cuota_total = Column(Integer, nullable=True)
    # Sin `ForeignKey()` a nivel de modelo (a diferencia de `categoria_id`/
    # `pagado_por`) deliberadamente: `0002_gastos.py` crea la tabla
    # `gastos` ANTES de que exista `Suscripcion` en el orden de
    # migraciones (`0009`), y una `ForeignKey` de SQLAlchemy exige que la
    # tabla referenciada ya esté registrada en `Base.metadata` en ese
    # momento — si no, `create_all`/`run_migrations` explota con
    # `NoReferencedTableError`. Mismo criterio que `cuota_grupo_id`
    # (columna plana, sin FK de SQLAlchemy). La integridad referencial
    # real en Postgres la agrega `0009_suscripciones.py` vía `ALTER TABLE
    # ... REFERENCES suscripciones(id)` (SQL crudo, no metadata de
    # SQLAlchemy) — ahí sí, porque para ese momento `suscripciones` ya
    # existe de verdad en la base.
    suscripcion_id = Column(GUID(), nullable=True)
    moneda = Column(String(3), nullable=False, default="ARS")

    participantes = relationship(
        "GastoParticipante", back_populates="gasto", cascade="all, delete-orphan"
    )

    def __repr__(self):  # pragma: no cover - solo para debugging
        return f"<Gasto id={self.id} descripcion={self.descripcion!r} importe={self.importe}>"


class GastoParticipante(Base):
    """La porción de un Gasto que le corresponde a un Miembro (REQ-004).

    Clave compuesta (gasto_id, miembro_id): un miembro participa a lo
    sumo una vez en cada gasto. Se fija en el momento del registro del
    gasto y nunca se recalcula retroactivamente (REQ-007).
    """

    __tablename__ = "gasto_participantes"

    gasto_id = Column(GUID(), ForeignKey("gastos.id"), primary_key=True)
    miembro_id = Column(GUID(), ForeignKey("miembros.id"), primary_key=True)
    monto_correspondiente = Column(Numeric(12, 2), nullable=False)

    gasto = relationship("Gasto", back_populates="participantes")

    def __repr__(self):  # pragma: no cover - solo para debugging
        return (
            f"<GastoParticipante gasto_id={self.gasto_id} miembro_id={self.miembro_id} "
            f"monto_correspondiente={self.monto_correspondiente}>"
        )
