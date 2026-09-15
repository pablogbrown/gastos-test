"""Migración: agrega las columnas `cuota_grupo_id`/`cuota_numero`/
`cuota_total` a `gastos` (spec `gastos-en-cuotas`).

Mismo patrón que `0006_miembro_desactivado_enum_value.py`/
`0007_miembro_email_invitacion.py`: una migración incremental y aditiva,
nunca recrear la tabla. `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` es
idempotente por diseño (relevante porque `main.py` corre `run_migrations`
en cada arranque) y está soportado nativamente por Postgres desde la
versión 9.6, sin necesitar inspeccionar las columnas existentes primero.

No-op en cualquier motor que no sea Postgres (SQLite, usado por toda la
suite de tests): ahí `Gasto.__table__` ya refleja las 3 columnas nuevas
desde la definición vigente del modelo, así que cualquier base de test
nueva las trae de entrada vía `create_all` — no hay nada que alterar.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade(bind: Engine) -> None:
    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        conn.execute(text("ALTER TABLE gastos ADD COLUMN IF NOT EXISTS cuota_grupo_id UUID"))
        conn.execute(text("ALTER TABLE gastos ADD COLUMN IF NOT EXISTS cuota_numero INTEGER"))
        conn.execute(text("ALTER TABLE gastos ADD COLUMN IF NOT EXISTS cuota_total INTEGER"))


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueven las columnas, mismo criterio que el resto
    # de las migraciones aditivas de este proyecto (ver `0006`/`0007`).
    pass
