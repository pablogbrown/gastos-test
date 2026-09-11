"""Migración inicial: crea las tablas `casas` y `miembros`.

No se introduce un motor de migraciones (p. ej. Alembic) en esta spec:
`upgrade`/`downgrade` operan directamente sobre `Base.metadata` para las
dos tablas de esta feature, lo cual alcanza el criterio "Done When" de
correr limpio sobre una base vacía. Si una spec futura necesita
migraciones incrementales más ricas, introducir Alembic es una decisión
de convención a tomar en ese momento, no aquí.

Nota (spec `usuarios-auth`, T1): `Miembro.usuario_id` es una FK a
`usuarios.id`. Como este proyecto no usa Alembic, `Miembro.__table__`
siempre refleja la definición *actual* del modelo — por eso, aunque esta
migración es anterior a `usuarios-auth`, ya la incluye en cualquier base
nueva. Se importa `Usuario` acá (mismo patrón que `0004_historial_
actividad.py`) únicamente para registrar su tabla en `Base.metadata`
antes de compilar el DDL de `miembros` — de lo contrario SQLAlchemy no
puede resolver la FK si este módulo se ejecuta de forma aislada, sin que
`0005_usuarios` se haya importado antes en el proceso.
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa
from src.db.models.miembro import Miembro
from src.db.models.usuario import Usuario  # noqa: F401 - registra la tabla referenciada (FK)

TABLES = [Casa.__table__, Miembro.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
