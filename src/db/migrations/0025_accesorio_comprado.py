"""Migración: crea `miembro_accesorio_comprado` (spec `tienda-accesorios`,
T2).

`MiembroAccesorioComprado.miembro_id`/`accesorio_id` llevan `ForeignKey()`
real a nivel de modelo — `miembros` (migración `0001`) y
`accesorios_avatar` (migración `0024`) son ambas anteriores a esta
`0025`, así que `create_all` resuelve esos `ForeignKey()` sin problema
([DBG-02]/[DBG-03] no aplica, mismo criterio que `0023_avatar_
seleccionado.py`).
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.accesorio_avatar import AccesorioAvatar  # noqa: F401 - registra la tabla referenciada
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada
from src.db.models.miembro_accesorio_comprado import MiembroAccesorioComprado

TABLES = [MiembroAccesorioComprado.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0024`).
    Base.metadata.drop_all(bind=bind, tables=TABLES)
