"""Migración: agrega la columna `email_invitacion` a `miembros` (spec
`invitar-miembro-pendiente`).

Mismo patrón que `0006_miembro_desactivado_enum_value.py`: una migración
incremental y aditiva, nunca recrear la tabla. `ALTER TABLE ... ADD
COLUMN IF NOT EXISTS` es idempotente por diseño (relevante porque
`main.py` corre `run_migrations` en cada arranque) y está soportado
nativamente por Postgres desde la versión 9.6, sin necesitar inspeccionar
las columnas existentes primero.

No-op en cualquier motor que no sea Postgres (SQLite, usado por toda la
suite de tests): ahí `Miembro.__table__` ya refleja `email_invitacion`
desde la definición vigente del modelo, así que cualquier base de test
nueva la trae de entrada vía `create_all` — no hay nada que alterar.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade(bind: Engine) -> None:
    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        conn.execute(
            text("ALTER TABLE miembros ADD COLUMN IF NOT EXISTS email_invitacion VARCHAR")
        )


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve la columna, mismo criterio que el resto de
    # las migraciones aditivas de este proyecto (ver `0006`).
    pass
