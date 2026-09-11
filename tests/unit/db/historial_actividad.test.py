"""T1 — Data Layer: HistorialActividad.

Cubre que la migración corre limpia sobre `casas`/`miembros` ya
sembrados y que una consulta ordenada por fecha descendente devuelve el
evento más reciente primero (TC-005).
"""
import importlib
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.casa import Casa
from src.db.models.historial_actividad import HistorialActividad, TipoActividadEnum
from src.db.models.miembro import Miembro, RolEnum

migracion_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
migracion_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migracion_casas.upgrade(engine)
    migracion_actividad.upgrade(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def test_migracion_de_actividad_corre_limpia_sobre_casas_miembros_ya_sembrados():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migracion_casas.upgrade(engine)
    # No debe lanzar sobre una base con `casas`/`miembros` ya creadas.
    migracion_actividad.upgrade(engine)


def test_historial_actividad_ordenado_por_fecha_descendente(session):
    casa = Casa(id=uuid.uuid4(), nombre="Casa Brown")
    session.add(casa)
    session.commit()

    ana = Miembro(
        id=uuid.uuid4(),
        casa_id=casa.id,
        nombre="Ana",
        identificacion="ANA1",
        rol=RolEnum.MEMBER,
    )
    session.add(ana)
    session.commit()

    ahora = datetime.now(timezone.utc)
    antigua = HistorialActividad(
        id=uuid.uuid4(),
        casa_id=casa.id,
        tipo=TipoActividadEnum.TAREA_CREADA,
        miembro_id=ana.id,
        fecha=ahora - timedelta(days=1),
        descripcion="Ana creó una tarea.",
    )
    reciente = HistorialActividad(
        id=uuid.uuid4(),
        casa_id=casa.id,
        tipo=TipoActividadEnum.GASTO_REGISTRADO,
        miembro_id=ana.id,
        fecha=ahora,
        descripcion="Ana registró un gasto.",
    )
    session.add_all([antigua, reciente])
    session.commit()

    filas = (
        session.query(HistorialActividad)
        .filter(HistorialActividad.casa_id == casa.id)
        .order_by(HistorialActividad.fecha.desc())
        .all()
    )

    assert [fila.id for fila in filas] == [reciente.id, antigua.id]


def test_historial_actividad_permite_miembro_id_nulo(session):
    casa = Casa(id=uuid.uuid4(), nombre="Casa Brown")
    session.add(casa)
    session.commit()

    entrada = HistorialActividad(
        id=uuid.uuid4(),
        casa_id=casa.id,
        tipo=TipoActividadEnum.MIEMBRO_AGREGADO,
        miembro_id=None,
        descripcion="Se agregó un miembro.",
    )
    session.add(entrada)
    session.commit()

    persisted = session.query(HistorialActividad).one()
    assert persisted.miembro_id is None
    assert persisted.fecha is not None
