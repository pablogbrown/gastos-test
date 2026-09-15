"""Migración: crea la tabla `suscripciones` y agrega `suscripcion_id` a
`gastos` (spec `gastos-suscripcion-mensual`, T1).

Combina los dos patrones ya usados por specs anteriores: `create_all`
para la tabla nueva (mismo criterio que `0004_historial_actividad.py`,
importando `Casa`/`Categoria`/`Miembro` para registrar las tablas
referenciadas) y `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` para la
columna aditiva en `gastos` (mismo criterio que `0008_gasto_cuotas.py`).

El `ALTER TABLE` es no-op en cualquier motor que no sea Postgres (SQLite,
usado por toda la suite de tests): ahí `Gasto.__table__` ya refleja
`suscripcion_id` desde la definición vigente del modelo, así que
cualquier base de test nueva la trae de entrada vía `create_all`.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada
from src.db.models.categoria import Categoria  # noqa: F401 - registra la tabla referenciada
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada
from src.db.models.suscripcion import Suscripcion

TABLES = [Suscripcion.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)

    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        # `CHAR(36)`, no `UUID`: `GUID()` (src/db/types.py) materializa
        # como `CHAR(36)` en Postgres (portabilidad con SQLite) — mismo
        # criterio que `0005_usuarios.py`'s `usuario_id CHAR(36)
        # REFERENCES usuarios(id)`. Un tipo `UUID` nativo acá rompería la
        # FK con "DatatypeMismatch" contra `suscripciones.id` (CHAR(36)).
        conn.execute(
            text(
                "ALTER TABLE gastos ADD COLUMN IF NOT EXISTS suscripcion_id CHAR(36) "
                "REFERENCES suscripciones(id)"
            )
        )


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve la columna, mismo criterio que el resto de
    # las migraciones aditivas de este proyecto (ver `0006`/`0007`/`0008`).
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
