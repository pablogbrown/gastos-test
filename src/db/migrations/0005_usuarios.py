"""Migración: agrega `Usuario` y la FK `Miembro.usuario_id` (spec `usuarios-auth`).

Sigue el mismo patrón sin motor de migraciones incremental que las
migraciones anteriores (ver docstring de `0001_casas_miembros.py`). A
diferencia de `0002`-`0004` (que solo agregan tablas nuevas), esta
migración también amplía una tabla ya existente (`miembros`) con una
columna nueva (`usuario_id`).

Como este proyecto no usa Alembic, `Miembro.__table__` ya refleja
`usuario_id` desde la definición vigente del modelo: en una base de test
recién creada, `0001` ya la trae al correr `create_all` sobre el modelo
actual. Esta migración verifica si la columna ya existe antes de
agregarla por `ALTER TABLE`, para cubrir ambos escenarios sin romper
ninguno:
- Base de test nueva (0001 ya creó `miembros` con la columna) → se
  omite el `ALTER TABLE`.
- Base real con las 4 migraciones anteriores ya aplicadas *antes* de que
  esta columna existiera (el escenario real que describe el "Done When"
  de T1) → se agrega por `ALTER TABLE`, nullable (no se fuerza backfill
  de datos históricos, ver Tradeoffs de `00-overview.md`).
"""
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada
from src.db.models.usuario import Usuario

TABLES = [Usuario.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)

    inspector = inspect(bind)
    columnas_miembro = {col["name"] for col in inspector.get_columns("miembros")}
    if "usuario_id" not in columnas_miembro:
        with bind.begin() as conn:
            conn.execute(
                text("ALTER TABLE miembros ADD COLUMN usuario_id CHAR(36) REFERENCES usuarios(id)")
            )


def downgrade(bind: Engine) -> None:
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
