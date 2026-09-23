"""Migración: crea `credito_transacciones` (spec `avatares-economia`, T1).

`CreditoTransaccion.casa_id`/`miembro_id` llevan `ForeignKey()` real a
nivel de modelo — igual que `LogroObtenido` en `0020_gamificacion.py`:
`casas`/`miembros` se crean en la migración `0001`, muy anterior a esta
`0021`, así que `create_all` resuelve esos `ForeignKey()` sin problema,
sin necesitar el patrón `[DBG-02]`/`[DBG-03]` (columna plana +
`ALTER TABLE` posterior).
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada por CreditoTransaccion.casa_id
from src.db.models.credito_transaccion import CreditoTransaccion
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada por CreditoTransaccion.miembro_id

TABLES = [CreditoTransaccion.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0020`).
    Base.metadata.drop_all(bind=bind, tables=TABLES)
