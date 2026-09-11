"""Migración inicial: crea las tablas `casas` y `miembros`.

No se introduce un motor de migraciones (p. ej. Alembic) en esta spec:
`upgrade`/`downgrade` operan directamente sobre `Base.metadata` para las
dos tablas de esta feature, lo cual alcanza el criterio "Done When" de
correr limpio sobre una base vacía. Si una spec futura necesita
migraciones incrementales más ricas, introducir Alembic es una decisión
de convención a tomar en ese momento, no aquí.
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa
from src.db.models.miembro import Miembro

TABLES = [Casa.__table__, Miembro.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
