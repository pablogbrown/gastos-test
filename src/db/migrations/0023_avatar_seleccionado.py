"""Migración: crea `miembro_avatar_seleccionado` (spec `avatares-economia`,
T3).

`MiembroAvatarSeleccionado.miembro_id`/`avatar_personaje_id` llevan
`ForeignKey()` real a nivel de modelo — `miembros` (migración `0001`) y
`avatar_personajes` (migración `0022`) son ambas anteriores a esta
`0023`, así que `create_all` resuelve esos `ForeignKey()` sin problema
([DBG-02]/[DBG-03] no aplica, mismo criterio que `0021_creditos.py`).
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.avatar_personaje import AvatarPersonaje  # noqa: F401 - registra la tabla referenciada
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada
from src.db.models.miembro_avatar_seleccionado import MiembroAvatarSeleccionado

TABLES = [MiembroAvatarSeleccionado.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0022`).
    Base.metadata.drop_all(bind=bind, tables=TABLES)
