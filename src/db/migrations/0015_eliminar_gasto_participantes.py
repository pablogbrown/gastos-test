"""Migración: elimina la tabla `gasto_participantes` (spec
`gastos-sin-reparto`, REQ-002).

Un gasto ya no se reparte entre participantes — `GastoParticipante` se
eliminó por completo del modelo (`src/db/models/gasto.py`), junto con
su historial (decisión explícita del usuario, no conservado). Esta
migración cierra el lado de la base de datos: `DROP TABLE IF EXISTS
gasto_participantes`, misma idempotencia por diseño que el resto de las
migraciones de este proyecto, pero a la inversa de las aditivas
(`0006`-`0013`).

Numerada `0015` (no `0014`, el número originalmente asumido al planear
esta spec en paralelo con `prestamos-entre-miembros`): esa spec hermana
tomó `0014` para su propia migración y mergeó a `main` primero — mismo
riesgo de colisión que su propio `Judgment` ya documentaba como
esperado. Renumerada al rebasear contra `main`.

No-op en cualquier base donde `gasto_participantes` nunca haya existido
(cualquier SQLite de test, o una base Postgres nueva creada después de
este cambio): `0002_gastos.py` ya no crea esa tabla, así que `IF EXISTS`
evita cualquier error. Relevante para una base Postgres real que ya la
tenía creada desde antes de este deploy (el volumen persistente de
`docker-compose` de este proyecto, o cualquier entorno productivo).
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade(bind: Engine) -> None:
    with bind.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS gasto_participantes"))


def downgrade(bind: Engine) -> None:
    # Destructiva por decisión explícita del usuario (spec
    # `gastos-sin-reparto`): el historial de reparto no se conserva, así
    # que no hay nada que recrear acá — mismo criterio que cualquier
    # migración de este proyecto que elimina en vez de agregar.
    pass
