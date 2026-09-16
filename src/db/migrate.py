"""Corre todas las migraciones de la app, en orden, contra un engine dado.

Sin Alembic (ver docstring de cada migración): cada módulo bajo
`src/db/migrations/` expone `upgrade(bind)`/`downgrade(bind)` operando
directamente sobre `Base.metadata`. Este helper es el único punto que
conoce el orden completo — usado por `src/api/main.py` al arrancar la
app, y equivalente al que cada archivo de test arma inline (los nombres
de módulo empiezan con dígitos, por eso `importlib` en vez de `import`).
"""
import importlib

from sqlalchemy.engine import Engine

_MIGRACIONES = (
    "0001_casas_miembros",
    "0002_gastos",
    "0003_tareas",
    "0004_historial_actividad",
    "0005_usuarios",
    "0006_miembro_desactivado_enum_value",
    "0007_miembro_email_invitacion",
    "0008_gasto_cuotas",
    "0009_suscripciones",
    "0010_gasto_suscripcion_moneda",
    "0011_tarjetas_credito",
    "0012_gasto_tarjeta_id",
    "0013_gasto_estado",
    "0014_prestamos",
    "0015_eliminar_gasto_participantes",
    "0016_prestamo_confirmacion",
)


def run_migrations(bind: Engine) -> None:
    for nombre in _MIGRACIONES:
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(bind)
