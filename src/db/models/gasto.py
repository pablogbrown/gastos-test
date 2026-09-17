import uuid

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String

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

    `tarjeta_id` (spec `importar-resumen-tarjeta`): `NULL` para un gasto
    no originado en la importación de un resumen; identifica de qué
    `TarjetaCredito` vino un consumo importado. Sin `ForeignKey()` a nivel
    de modelo, mismo criterio que `suscripcion_id`/`cuota_grupo_id` de
    arriba — la integridad referencial real en Postgres la agrega
    `0012_gasto_tarjeta_id.py` vía `ALTER TABLE ... REFERENCES
    tarjetas_credito(id)` (SQL crudo, no metadata de SQLAlchemy), evitando
    depender de que `tarjeta_credito.py` ya esté importado en todo
    contexto donde se importe este módulo.

    `estado` (spec `gastos-estado-pago`): `"pagado"` (default) o
    `"a_pagar"` -- puramente informativo, no afecta ningun calculo de
    `balance_service`. Un gasto cargado a mano nace `"pagado"`; un gasto
    generado automaticamente (cuota futura, suscripcion mensual, consumo
    importado de un resumen) nace `"a_pagar"`. Columna `String` simple,
    sin enum nativo de Postgres -- mismo criterio que `moneda`.

    `resumen_id` (spec `resumen-tarjeta-pago`): `NULL` para un gasto no
    originado en la importación de un resumen; identifica de qué
    `ResumenTarjeta` vino un consumo importado, para que `pagar_resumen`
    pueda marcar de una sola vez todos los gastos de ese resumen como
    pagados. Sin `ForeignKey()` a nivel de modelo, mismo criterio que
    `tarjeta_id`/`suscripcion_id` de arriba: `gastos` se crea en la
    migración `0002`, mucho antes que `resumenes_tarjeta` (`0019`), y una
    `ForeignKey` de SQLAlchemy exige que la tabla referenciada ya esté
    registrada en `Base.metadata` en ese momento — no lo está. La
    integridad referencial real en Postgres la agrega `0019_resumen_
    tarjeta.py` vía `ALTER TABLE ... REFERENCES resumenes_tarjeta(id)`
    (SQL crudo, no metadata de SQLAlchemy), después de crear esa tabla en
    esa misma migración.
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
    tarjeta_id = Column(GUID(), nullable=True)
    estado = Column(String, nullable=False, default="pagado")
    resumen_id = Column(GUID(), nullable=True)

    def __repr__(self):  # pragma: no cover - solo para debugging
        return f"<Gasto id={self.id} descripcion={self.descripcion!r} importe={self.importe}>"
