"""T1 — Data Layer: Casa y Miembro.

Cubre TC-001 (creación válida), TC-004 (identificación duplicada rechazada
por constraint) y TC-009 (misma identificación permitida en casas
distintas), a nivel de esquema de datos.
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.casa import Casa
from src.db.models.miembro import Miembro, RolEnum

migration = importlib.import_module("src.db.migrations.0001_casas_miembros")


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration.upgrade(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def test_migracion_corre_limpia_sobre_base_vacia():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # No debe lanzar sobre una base recién creada.
    migration.upgrade(engine)


def test_crear_casa_y_miembro_validos(session):
    casa = Casa(id=uuid.uuid4(), nombre="Casa Brown")
    session.add(casa)
    session.commit()

    miembro = Miembro(
        id=uuid.uuid4(),
        casa_id=casa.id,
        nombre="Pablo",
        identificacion="P1",
        rol=RolEnum.ADMIN,
    )
    session.add(miembro)
    session.commit()

    assert session.query(Casa).count() == 1
    assert session.query(Miembro).count() == 1
    persisted = session.query(Miembro).one()
    assert persisted.activo is True
    assert persisted.rol == RolEnum.ADMIN
    assert persisted.casa_id == casa.id


def test_identificacion_duplicada_en_misma_casa_falla_constraint(session):
    casa = Casa(id=uuid.uuid4(), nombre="Casa Brown")
    session.add(casa)
    session.commit()

    session.add(
        Miembro(
            id=uuid.uuid4(),
            casa_id=casa.id,
            nombre="Ana",
            identificacion="P1",
            rol=RolEnum.MEMBER,
        )
    )
    session.commit()

    session.add(
        Miembro(
            id=uuid.uuid4(),
            casa_id=casa.id,
            nombre="Otra Ana",
            identificacion="P1",
            rol=RolEnum.MEMBER,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_misma_identificacion_permitida_en_casas_distintas(session):
    casa_1 = Casa(id=uuid.uuid4(), nombre="Casa Brown")
    casa_2 = Casa(id=uuid.uuid4(), nombre="Casa Verde")
    session.add_all([casa_1, casa_2])
    session.commit()

    session.add(
        Miembro(
            id=uuid.uuid4(),
            casa_id=casa_1.id,
            nombre="Ana",
            identificacion="P1",
            rol=RolEnum.ADMIN,
        )
    )
    session.add(
        Miembro(
            id=uuid.uuid4(),
            casa_id=casa_2.id,
            nombre="Bruno",
            identificacion="P1",
            rol=RolEnum.ADMIN,
        )
    )
    # No debe lanzar: la unicidad es por (casa_id, identificacion).
    session.commit()

    assert session.query(Miembro).count() == 2
