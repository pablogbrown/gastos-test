"""Migración: crea la tabla `tarjetas_credito` (spec `tarjetas-credito`,
T1).

`create_all` para la tabla nueva, mismo patrón que `0009_suscripciones.py`
— importando `Casa`/`Miembro` para registrar las tablas referenciadas por
las FKs reales (`casas`/`miembros` ya existen en el orden de migraciones,
así que no aplica el problema de `NoReferencedTableError` documentado
para `Gasto.suscripcion_id`).
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada
from src.db.models.tarjeta_credito import TarjetaCredito

TABLES = [TarjetaCredito.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0010`).
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
