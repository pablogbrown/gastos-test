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
nueva. Por eso `Usuario.__table__` se crea acá también (antes que
`miembros`, por la FK): en PostgreSQL, a diferencia de SQLite, `CREATE
TABLE ... REFERENCES usuarios(id)` falla en el momento si la tabla
referenciada no existe todavía — solo importar el modelo (como se hacía
antes) alcanza para que SQLAlchemy compile el DDL, pero no crea la
tabla en la base real. `0005_usuarios.upgrade()` vuelve a llamar
`create_all` sobre `Usuario.__table__`, que ya es un no-op aquí (`create_all`
solo crea lo que no existe) — cubre el caso de una base que corrió `0001`-`0004`
antes de que existiera esta spec.
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa
from src.db.models.miembro import Miembro
from src.db.models.usuario import Usuario

TABLES = [Casa.__table__, Usuario.__table__, Miembro.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
