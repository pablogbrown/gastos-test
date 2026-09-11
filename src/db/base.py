"""Engine y sesión de base de datos compartidos por toda la capa de servicios.

DATABASE_URL apunta a PostgreSQL en producción (ver .nybo/foundation/stack.yaml).
Por defecto usa un SQLite en memoria compartido entre conexiones, lo que
permite que los tests unitarios/integración de esta spec corran sin
depender de un PostgreSQL real.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

_engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_session():
    """Devuelve una nueva sesión ligada al engine configurado."""
    return SessionLocal()
