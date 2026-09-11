"""Migración: crea la tabla `historial_actividad`.

Sigue el mismo patrón sin motor de migraciones incremental que
`0001_casas_miembros.py`: `upgrade`/`downgrade` operan directamente sobre
`Base.metadata` para la tabla de esta spec. El número `0004` continúa la
secuencia reservada por las specs hermanas ya fusionadas en
`feat/gestion-domestica` (`0002_gastos`, `0003_tareas`).

Requiere que `casas` y `miembros` (migración `0001`) ya existan, ya que
`historial_actividad.casa_id`/`miembro_id` referencian esas tablas.
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada
from src.db.models.historial_actividad import HistorialActividad

TABLES = [HistorialActividad.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
