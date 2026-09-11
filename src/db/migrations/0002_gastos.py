"""Migración: crea `categorias`, `gastos` y `gasto_participantes`.

Sigue el mismo patrón sin motor de migraciones que
`0001_casas_miembros.py`: `upgrade`/`downgrade` operan directamente sobre
`Base.metadata` para las tablas de esta feature.

Además de crear las tablas, `upgrade` siembra las 8 categorías
predefinidas del documento fuente en cada casa que ya existiera al
momento de migrar (las casas creadas después de esta migración arman su
catálogo vía `crear_categoria`). La siembra es idempotente: correr la
migración más de una vez no duplica categorías ya presentes en una casa
("Done When" de T1).
"""
import uuid

from sqlalchemy import select
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa
from src.db.models.categoria import CATEGORIAS_PREDEFINIDAS, Categoria
from src.db.models.gasto import Gasto, GastoParticipante

TABLES = [Categoria.__table__, Gasto.__table__, GastoParticipante.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)
    _seed_categorias_predefinidas(bind)


def downgrade(bind: Engine) -> None:
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))


def _seed_categorias_predefinidas(bind: Engine) -> None:
    with bind.begin() as conn:
        casa_ids = [row[0] for row in conn.execute(select(Casa.id))]
        for casa_id in casa_ids:
            existentes = {
                row[0]
                for row in conn.execute(
                    select(Categoria.nombre).where(Categoria.casa_id == casa_id)
                )
            }
            for nombre in CATEGORIAS_PREDEFINIDAS:
                if nombre in existentes:
                    continue
                conn.execute(
                    Categoria.__table__.insert().values(
                        id=uuid.uuid4(), casa_id=casa_id, nombre=nombre
                    )
                )
