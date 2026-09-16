"""Migracion: agrega la columna `estado` a `gastos` (spec
`gastos-estado-pago`, T1).

Mismo patron que `0010_gasto_suscripcion_moneda.py`: una migracion
incremental y aditiva, nunca recrear la tabla. `ALTER TABLE ... ADD
COLUMN IF NOT EXISTS ... DEFAULT 'pagado'` es idempotente por diseno y
soportado nativamente por Postgres desde la version 9.6.

No-op en cualquier motor que no sea Postgres (SQLite, usado por toda la
suite de tests): ahi `Gasto.__table__` ya refleja la columna `estado`
desde la definicion vigente del modelo, asi que cualquier base de test
nueva la trae de entrada via `create_all` -- no hay nada que alterar.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade(bind: Engine) -> None:
    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE gastos ADD COLUMN IF NOT EXISTS estado VARCHAR "
                "NOT NULL DEFAULT 'pagado'"
            )
        )


def downgrade(bind: Engine) -> None:
    # Aditivo -- no se remueve la columna, mismo criterio que el resto de
    # las migraciones aditivas de este proyecto (ver `0006`-`0012`).
    pass
