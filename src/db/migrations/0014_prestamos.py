"""Migración: crea la tabla `prestamos` (spec `prestamos-entre-miembros`,
T1).

`create_all` para la tabla nueva, mismo patrón que `0011_tarjetas_
credito.py` — importando `Casa`/`Miembro` para registrar las tablas
referenciadas por las FKs reales (`casas`/`miembros` ya existen en el
orden de migraciones, así que no aplica el problema de
`NoReferencedTableError` documentado para `Gasto.suscripcion_id`).

Nota de numeración: el plan original de la spec asumía `0015` como
próximo número libre, pero al implementar el próximo número libre real
era `0014` (`0013_gasto_estado` es la última migración existente en esta
rama) — la spec hermana `gastos-sin-reparto` (independiente, sin
dependencia funcional con esta) se construye en paralelo y puede
introducir su propia migración antes o después; una colisión de
numeración al mergear `main` es esperable y se resuelve en ese momento
(ver `01-plan-01-modelo-prestamo.md`).
"""
from sqlalchemy.engine import Engine

from src.db.base import Base
from src.db.models.casa import Casa  # noqa: F401 - registra la tabla referenciada
from src.db.models.miembro import Miembro  # noqa: F401 - registra la tabla referenciada
from src.db.models.prestamo import Prestamo

TABLES = [Prestamo.__table__]


def upgrade(bind: Engine) -> None:
    Base.metadata.create_all(bind=bind, tables=TABLES)


def downgrade(bind: Engine) -> None:
    # Aditivo — no se remueve, mismo criterio que el resto de las
    # migraciones aditivas de este proyecto (ver `0006`-`0011`).
    Base.metadata.drop_all(bind=bind, tables=list(reversed(TABLES)))
