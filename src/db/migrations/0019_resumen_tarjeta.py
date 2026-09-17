"""Migración: crea la tabla `resumenes_tarjeta` y agrega `gastos.resumen_id`
(spec `resumen-tarjeta-pago`, T1).

Una sola migración para ambos cambios de esquema — están estrechamente
acoplados (la columna no tiene sentido sin la tabla) y siempre se
shippean juntos, mismo criterio que `0018_mantenimiento_autos.py` con
`auto_id`/`autos`.

`Gasto.resumen_id` (`src/db/models/gasto.py`) es un `Column` plano, sin
`ForeignKey()` a nivel de modelo — ver su propio docstring y
`[DBG-02]`/`[DBG-03]` (`.nybo/memory/domains/db.md`): la migración que
crea `gastos` (`0002_gastos.py`) corre ANTES que esta, y su `create_all`
resuelve `Gasto.__table__` contra el modelo vigente — que ya incluye
`resumen_id` desde que se agregó al archivo del modelo. Un
`ForeignKey("resumenes_tarjeta.id")` real a nivel de modelo haría fallar
`0002.upgrade()` en cualquier base creada desde cero con
`relation "resumenes_tarjeta" does not exist` (esa tabla todavía no
existe en ese punto de `run_migrations`). El FK real se agrega acá, vía
SQL crudo, DESPUÉS de crear `resumenes_tarjeta` en esta misma migración
(mismo patrón que `0009_suscripciones.py`/`0012_gasto_tarjeta_id.py`/
`0018_mantenimiento_autos.py`).

El `ALTER TABLE` es no-op en cualquier motor que no sea Postgres (SQLite,
usado por toda la suite de tests): ahí `Gasto.__table__` ya refleja
`resumen_id` desde la definición vigente del modelo, así que cualquier
base de test nueva la trae de entrada vía `create_all` de `0002`. Mismo
gap ya aceptado y documentado (`[DBG-04]`): en una base creada desde cero
por `run_migrations` en una sola pasada, `0002` ya crea la columna (sin
el constraint) y el `ADD COLUMN IF NOT EXISTS` de acá es un no-op — el FK
real solo se adjunta en el path real de producción (una base que ya
tenía `gastos` sin `resumen_id` antes de este deploy).
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada por ResumenTarjeta.casa_id
from src.db.models.resumen_tarjeta import ResumenTarjeta
from src.db.models.tarjeta_credito import TarjetaCredito  # noqa: F401 - registra la tabla referenciada por ResumenTarjeta.tarjeta_id

TABLES = [ResumenTarjeta.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)

    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        # `CHAR(36)`, no `UUID`: `GUID()` (src/db/types.py) materializa
        # como `CHAR(36)` en Postgres (portabilidad con SQLite) — mismo
        # criterio que `0012_gasto_tarjeta_id.py`'s `tarjeta_id CHAR(36)
        # REFERENCES tarjetas_credito(id)`.
        conn.execute(
            text(
                "ALTER TABLE gastos ADD COLUMN IF NOT EXISTS resumen_id "
                "CHAR(36) REFERENCES resumenes_tarjeta(id)"
            )
        )


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0018`).
    Base.metadata.drop_all(bind=bind, tables=TABLES)
