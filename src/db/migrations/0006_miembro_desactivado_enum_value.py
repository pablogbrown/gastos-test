"""Migración: agrega el valor `miembro_desactivado` al tipo enum nativo de
Postgres `tipoactividadenum`, para un entorno donde `historial_actividad`
ya existe con datos persistidos (spec
`fix-historial-desactivacion-miembro`).

Por qué hace falta (hallazgo del smoke test en vivo de esa spec, contra el
Postgres real de `docker-compose`, con datos ya existentes en el volumen):
`0004_historial_actividad.upgrade` usa `Base.metadata.create_all`, que
solo actúa si la tabla `historial_actividad` no existe todavía. En un
entorno donde esa tabla ya fue creada (por ejemplo, el volumen persistente
de `docker-compose` de este proyecto, levantado antes de este fix),
`create_all` no toca el tipo enum nativo ya existente en Postgres, sin
importar qué valores tenga hoy `TipoActividadEnum` en Python — agregar
`MIEMBRO_DESACTIVADO` al enum de Python no alcanza para que Postgres lo
acepte, y `desactivar_miembro` falla con
`psycopg2.errors.InvalidTextRepresentation` al intentar registrar la
actividad. El Tradeoff de la spec ya anticipaba este gap para producción;
este archivo lo cierra con una migración real en vez de dejarlo solo
documentado, porque el propio entorno de desarrollo dockerizado del
proyecto ya lo pisa.

`ALTER TYPE ... ADD VALUE IF NOT EXISTS` es seguro de re-ejecutar
(idempotente) y no requiere recrear el esquema ni perder datos. Corre
fuera de una transacción explícita (`AUTOCOMMIT`) porque versiones de
Postgres anteriores a la 12 no permiten `ALTER TYPE ADD VALUE` dentro de
un bloque de transacción — evitarlo también acá mantiene esta migración
portable sin depender de la versión exacta del servidor.

No-op en cualquier motor que no sea Postgres (SQLite, usado por toda la
suite de tests): ahí `Enum(TipoActividadEnum)` no crea un tipo nativo — la
tabla siempre se crea desde cero reflejando el `TipoActividadEnum` vigente
en Python, así que no hay nada que alterar.
"""
from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade(bind: Engine) -> None:
    if bind.dialect.name != "postgresql":
        return
    # El tipo enum nativo de Postgres almacena el *nombre* del miembro del
    # enum de Python (`MIEMBRO_DESACTIVADO`), no su `.value`
    # (`"miembro_desactivado"`) — mismo comportamiento por defecto de
    # SQLAlchemy que ya rige los 5 valores existentes del tipo
    # (`GASTO_REGISTRADO`, `TAREA_CREADA`, etc.), todos en mayúsculas.
    with bind.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(
            text("ALTER TYPE tipoactividadenum ADD VALUE IF NOT EXISTS 'MIEMBRO_DESACTIVADO'")
        )


def downgrade(bind: Engine) -> None:
    # Postgres no permite remover un valor de un enum nativo sin recrear
    # el tipo entero (y todas las columnas que lo usan) — no-op deliberado,
    # igual criterio que el resto de las migraciones de este proyecto para
    # cambios de tipo aditivos.
    pass
