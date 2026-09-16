"""Migración: crea la tabla `autos` y agrega `items_mantenimiento.auto_id`
(spec `mantenimiento-autos`, T1).

Una sola migración para ambos cambios de esquema — están estrechamente
acoplados (la columna no tiene sentido sin la tabla) y siempre se
shippean juntos, mismo criterio que `0009_suscripciones.py` (tabla nueva
+ columna aditiva en un modelo ya existente en la misma migración).

`ItemMantenimiento.auto_id` (`src/db/models/mantenimiento.py`) es un
`Column` plano, sin `ForeignKey()` a nivel de modelo — ver su propio
docstring y `[DBG-02]`/`[DBG-03]` (`.nybo/memory/domains/db.md`): la
migración que crea `items_mantenimiento` (`0017_mantenimiento.py`) corre
ANTES que esta, y su `create_all` resuelve `ItemMantenimiento.__table__`
contra el modelo vigente — que ya incluye `auto_id` desde que se agregó
al archivo del modelo. Un `ForeignKey("autos.id")` real a nivel de
modelo haría fallar `0017.upgrade()` en cualquier base creada desde cero
con `relation "autos" does not exist` (`autos` todavía no existe en ese
punto de `run_migrations`). El FK real se agrega acá, vía SQL crudo,
DESPUÉS de crear `autos` en esta misma migración (mismo patrón que
`0009_suscripciones.py`/`0012_gasto_tarjeta_id.py`).

El `ALTER TABLE` es no-op en cualquier motor que no sea Postgres (SQLite,
usado por toda la suite de tests): ahí `ItemMantenimiento.__table__` ya
refleja `auto_id` desde la definición vigente del modelo, así que
cualquier base de test nueva la trae de entrada vía `create_all` de
`0017`. Mismo gap ya aceptado y documentado (`[DBG-04]`): en una base
creada desde cero por `run_migrations` en una sola pasada, `0017` ya crea
la columna (sin el constraint) y el `ADD COLUMN IF NOT EXISTS` de acá es
un no-op — el FK real solo se adjunta en el path real de producción (una
base que ya tenía `items_mantenimiento` sin `auto_id` antes de este
deploy).
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.auto import Auto
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada por Auto.casa_id

TABLES = [Auto.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)

    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        # `CHAR(36)`, no `UUID`: `GUID()` (src/db/types.py) materializa
        # como `CHAR(36)` en Postgres (portabilidad con SQLite) — mismo
        # criterio que `0009_suscripciones.py`'s `suscripcion_id CHAR(36)
        # REFERENCES suscripciones(id)`.
        conn.execute(
            text(
                "ALTER TABLE items_mantenimiento ADD COLUMN IF NOT EXISTS auto_id "
                "CHAR(36) REFERENCES autos(id)"
            )
        )


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0017`).
    Base.metadata.drop_all(bind=bind, tables=TABLES)
