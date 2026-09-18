"""Migración: crea `logros_obtenidos` y agrega `Casa.meta_puntos_mensual`
(spec `gamificacion-puntos`, T2/T3).

Una sola migración para ambos cambios de esquema — chicos, estrechamente
relacionados (misma spec) y se shippean juntos, mismo criterio que
`0018_mantenimiento_autos.py`/`0019_resumen_tarjeta.py`.

`LogroObtenido.casa_id`/`miembro_id` (`src/db/models/logro_obtenido.py`)
SÍ llevan `ForeignKey()` real a nivel de modelo — a diferencia de
`Gasto.resumen_id`/`tarjeta_id`, acá no hay ningún riesgo de
FK-ordering: `casas`/`miembros` se crean en la migración `0001`, muy
anterior a esta `0020` — `create_all` de esta migración resuelve esos
`ForeignKey()` sin problema, sin necesitar SQL crudo posterior (ver
[DBG-02]/[DBG-03], `.nybo/memory/domains/db.md`).

`Casa.meta_puntos_mensual` es una columna nueva NULLABLE en una tabla ya
existente — igual que `Gasto.estado` en su momento: se agrega directo a
la clase del modelo, y `create_all`/`ALTER TABLE ... ADD COLUMN IF NOT
EXISTS` la crea bien tanto en una base nueva como en una ya existente.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada por LogroObtenido.casa_id
from src.db.models.logro_obtenido import LogroObtenido
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada por LogroObtenido.miembro_id

TABLES = [LogroObtenido.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)

    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        conn.execute(
            text("ALTER TABLE casas ADD COLUMN IF NOT EXISTS meta_puntos_mensual INTEGER")
        )


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0019`).
    Base.metadata.drop_all(bind=bind, tables=TABLES)
