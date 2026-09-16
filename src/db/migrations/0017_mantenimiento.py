"""Migración: crea las tablas `items_mantenimiento`/`materiales_
mantenimiento` (spec `mantenimiento-casa`, T1).

`create_all` para las tablas nuevas, mismo patrón que `0011_tarjetas_
credito.py`/`0014_prestamos.py` — importando `Casa` para registrar la
tabla referenciada por la FK real (`casas` ya existe en el orden de
migraciones, así que no aplica el problema de `NoReferencedTableError`
documentado para `Gasto.suscripcion_id`). `materiales_mantenimiento`
referencia `items_mantenimiento`, creada en esta misma migración antes
que `create_all` resuelva las FKs (ambas tablas están en `TABLES`, en
orden).
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada
from src.db.models.mantenimiento import ItemMantenimiento, MaterialMantenimiento

TABLES = [ItemMantenimiento.__table__, MaterialMantenimiento.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0016`).
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
