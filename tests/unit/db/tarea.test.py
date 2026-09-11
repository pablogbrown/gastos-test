"""T1 — Data Layer: Tarea e HistorialTarea.

Cubre TC-003 (estado por defecto = pendiente) y que la migración de
tareas corre limpia sobre una base con casas/miembros ya sembrados.
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.casa import Casa
from src.db.models.historial_tarea import HistorialTarea
from src.db.models.miembro import Miembro, RolEnum
from src.db.models.tarea import EstadoTareaEnum, Tarea

migracion_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
migracion_tareas = importlib.import_module("src.db.migrations.0003_tareas")


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migracion_casas.upgrade(engine)
    migracion_tareas.upgrade(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def test_migracion_de_tareas_corre_limpia_sobre_casas_miembros_ya_sembrados():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migracion_casas.upgrade(engine)
    # No debe lanzar sobre una base con `casas`/`miembros` ya creadas.
    migracion_tareas.upgrade(engine)


def test_tarea_creada_sin_estado_explicito_queda_pendiente(session):
    casa = Casa(id=uuid.uuid4(), nombre="Casa Brown")
    session.add(casa)
    session.commit()

    admin = Miembro(
        id=uuid.uuid4(),
        casa_id=casa.id,
        nombre="Administrador",
        identificacion="A1",
        rol=RolEnum.ADMIN,
    )
    session.add(admin)
    session.commit()

    tarea = Tarea(id=uuid.uuid4(), casa_id=casa.id, nombre="Lavar los platos", puntos=5)
    session.add(tarea)
    session.commit()

    persisted = session.query(Tarea).one()
    assert persisted.estado == EstadoTareaEnum.PENDIENTE
    assert persisted.recurrente is False
    assert persisted.responsable_id is None


def test_historial_tarea_registra_finalizacion(session):
    casa = Casa(id=uuid.uuid4(), nombre="Casa Brown")
    session.add(casa)
    session.commit()

    miembro = Miembro(
        id=uuid.uuid4(),
        casa_id=casa.id,
        nombre="Ana",
        identificacion="ANA1",
        rol=RolEnum.MEMBER,
    )
    session.add(miembro)
    session.commit()

    tarea = Tarea(id=uuid.uuid4(), casa_id=casa.id, nombre="Sacar la basura", puntos=5)
    session.add(tarea)
    session.commit()

    historial = HistorialTarea(
        id=uuid.uuid4(), tarea_id=tarea.id, miembro_id=miembro.id, puntos_obtenidos=5
    )
    session.add(historial)
    session.commit()

    persisted = session.query(HistorialTarea).one()
    assert persisted.puntos_obtenidos == 5
    assert persisted.completada_en is not None
    assert persisted.miembro_id == miembro.id
