"""Migración: crea las tablas `tareas` y `historial_tarea`.

Sigue el mismo patrón que `0001_casas_miembros.py`: sin motor de
migraciones incremental, `upgrade`/`downgrade` operan directamente sobre
`Base.metadata` para las tablas de esta spec. El número `0003` (en vez de
`0002`) es intencional: la spec hermana `gastos`, construida en paralelo
sobre la misma base `feat/gestion-domestica`, reserva `0002` para su propia
migración — así ambas ramas pueden fusionarse sin colisión de nombres de
archivo.

Requiere que `casas` y `miembros` (migración `0001`) ya existan, ya que
`tareas.casa_id`/`responsable_id` y `historial_tarea.miembro_id`
referencian esas tablas.
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada
from src.db.models.historial_tarea import HistorialTarea
from src.db.models.tarea import Tarea

TABLES = [Tarea.__table__, HistorialTarea.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
