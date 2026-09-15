"""Migración: agrega la columna `moneda` a `gastos` y `suscripciones`
(spec `gastos-multi-moneda`, T1).

Mismo patrón que `0008_gasto_cuotas.py`/`0009_suscripciones.py`: una
migración incremental y aditiva, nunca recrear la tabla. `ALTER TABLE
... ADD COLUMN IF NOT EXISTS ... DEFAULT 'ARS'` es idempotente por
diseño y soportado nativamente por Postgres desde la versión 9.6.

No-op en cualquier motor que no sea Postgres (SQLite, usado por toda la
suite de tests): ahí `Gasto.__table__`/`Suscripcion.__table__` ya
reflejan la columna `moneda` desde la definición vigente del modelo, así
que cualquier base de test nueva la trae de entrada vía `create_all` —
no hay nada que alterar.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade(bind: Engine) -> None:
    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE gastos ADD COLUMN IF NOT EXISTS moneda VARCHAR(3) "
                "NOT NULL DEFAULT 'ARS'"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE suscripciones ADD COLUMN IF NOT EXISTS moneda VARCHAR(3) "
                "NOT NULL DEFAULT 'ARS'"
            )
        )


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueven las columnas, mismo criterio que el resto
    # de las migraciones aditivas de este proyecto (ver `0006`-`0009`).
    pass
