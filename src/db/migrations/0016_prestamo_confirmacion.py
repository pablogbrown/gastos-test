"""Migración: agrega `confirmado_prestamista`/`confirmado_deudor` a
`prestamos` (spec `prestamos-confirmacion-mutua`, T1).

Mismo patrón que `0013_gasto_estado.py`: una migración incremental y
aditiva, nunca recrear la tabla. `ALTER TABLE ... ADD COLUMN IF NOT
EXISTS ...` es idempotente por diseño. A diferencia de `0013`, estas dos
columnas NO llevan `DEFAULT` — son `NULL`able sin default porque `NULL`
ES el estado "pendiente de confirmar" (ver `Prestamo.estado_confirmacion`
y Tradeoffs de `00-overview.md`), nunca un valor a rellenar.

No-op en cualquier motor que no sea Postgres (SQLite, usado por toda la
suite de tests): ahí `Prestamo.__table__` ya refleja las columnas nuevas
desde la definición vigente del modelo, así que cualquier base de test
nueva las trae de entrada vía `create_all` — no hay nada que alterar.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade(bind: Engine) -> None:
    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        conn.execute(
            text("ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS confirmado_prestamista BOOLEAN")
        )
        conn.execute(
            text("ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS confirmado_deudor BOOLEAN")
        )


def downgrade(bind: Engine) -> None:
    # Aditivo -- no se remueve la columna, mismo criterio que el resto de
    # las migraciones aditivas de este proyecto (ver `0006`-`0013`).
    pass
