"""Migración: agrega la columna `tarjeta_id` a `gastos` (spec
`importar-resumen-tarjeta`, T1).

Mismo patrón que `0009_suscripciones.py`'s `ALTER TABLE ... ADD COLUMN
... REFERENCES`: `tarjetas_credito` ya existe en la base para cuando esta
migración corre (creada por `0011_tarjetas_credito.py`), así que la FK
real se agrega acá vía SQL crudo — no como `ForeignKey()` a nivel de
modelo (ver docstring de `Gasto.tarjeta_id`, mismo criterio que
`suscripcion_id`: evita depender de que `tarjeta_credito.py` esté
importado en todo contexto donde se registra `Gasto` en `Base.metadata`).

No-op en cualquier motor que no sea Postgres (SQLite, usado por toda la
suite de tests): ahí `Gasto.__table__` ya refleja `tarjeta_id` desde la
definición vigente del modelo, así que cualquier base de test nueva la
trae de entrada vía `create_all` — no hay nada que alterar.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade(bind: Engine) -> None:
    if bind.dialect.name != "postgresql":
        return
    with bind.begin() as conn:
        # `CHAR(36)`, no `UUID`: `GUID()` (src/db/types.py) materializa
        # como `CHAR(36)` en Postgres (portabilidad con SQLite) — mismo
        # criterio que `0009_suscripciones.py`'s `suscripcion_id CHAR(36)
        # REFERENCES suscripciones(id)`.
        conn.execute(
            text(
                "ALTER TABLE gastos ADD COLUMN IF NOT EXISTS tarjeta_id CHAR(36) "
                "REFERENCES tarjetas_credito(id)"
            )
        )


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve la columna, mismo criterio que el resto de
    # las migraciones aditivas de este proyecto (ver `0006`-`0011`).
    pass
