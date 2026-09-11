"""T1 — Data Layer: Gasto, Categoria y GastoParticipante.

Cubre TC-001 (inserción válida) y TC-006 (la suma de las partes de un
gasto puede compararse contra su importe) a nivel de esquema, más la
siembra idempotente de categorías predefinidas requerida por el "Done
When" de T1.
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.casa import Casa
from src.db.models.categoria import CATEGORIAS_PREDEFINIDAS, Categoria
from src.db.models.gasto import Gasto, GastoParticipante
from src.db.models.miembro import Miembro, RolEnum

migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas.upgrade(eng)
    migration_gastos.upgrade(eng)
    return eng


@pytest.fixture()
def session(engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def _crear_casa_con_miembro(session, nombre_casa="Casa Brown"):
    casa = Casa(id=uuid.uuid4(), nombre=nombre_casa)
    session.add(casa)
    session.commit()

    miembro = Miembro(
        id=uuid.uuid4(),
        casa_id=casa.id,
        nombre="Pablo",
        identificacion=f"P-{uuid.uuid4()}",
        rol=RolEnum.ADMIN,
    )
    session.add(miembro)
    session.commit()
    return casa, miembro


def test_migracion_de_gastos_corre_limpia_sobre_base_vacia():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas.upgrade(eng)
    # No debe lanzar sobre una base recién creada.
    migration_gastos.upgrade(eng)


def test_insertar_gasto_y_participante_consistentes(session):
    casa, miembro = _crear_casa_con_miembro(session)
    categoria = Categoria(id=uuid.uuid4(), casa_id=casa.id, nombre="Supermercado")
    session.add(categoria)
    session.commit()

    gasto = Gasto(
        id=uuid.uuid4(),
        casa_id=casa.id,
        descripcion="Compra semanal",
        importe=Decimal("100.00"),
        fecha=date(2026, 1, 1),
        pagado_por=miembro.id,
        categoria_id=categoria.id,
    )
    session.add(gasto)
    session.commit()

    participante = GastoParticipante(
        gasto_id=gasto.id, miembro_id=miembro.id, monto_correspondiente=Decimal("100.00")
    )
    session.add(participante)
    session.commit()

    persisted = session.query(Gasto).one()
    assert persisted.descripcion == "Compra semanal"
    assert persisted.importe == Decimal("100.00")
    assert len(persisted.participantes) == 1
    assert persisted.participantes[0].monto_correspondiente == Decimal("100.00")


def test_suma_de_participantes_puede_compararse_contra_el_importe(session):
    casa, miembro = _crear_casa_con_miembro(session)
    categoria = Categoria(id=uuid.uuid4(), casa_id=casa.id, nombre="Comida")
    session.add(categoria)
    session.commit()

    otro_miembro = Miembro(
        id=uuid.uuid4(),
        casa_id=casa.id,
        nombre="Ana",
        identificacion=f"A-{uuid.uuid4()}",
        rol=RolEnum.MEMBER,
    )
    session.add(otro_miembro)
    session.commit()

    gasto = Gasto(
        id=uuid.uuid4(),
        casa_id=casa.id,
        descripcion="Cena",
        importe=Decimal("40000.00"),
        fecha=date(2026, 1, 2),
        pagado_por=miembro.id,
        categoria_id=categoria.id,
    )
    session.add(gasto)
    session.commit()

    session.add_all(
        [
            GastoParticipante(
                gasto_id=gasto.id, miembro_id=miembro.id, monto_correspondiente=Decimal("20000.00")
            ),
            GastoParticipante(
                gasto_id=gasto.id,
                miembro_id=otro_miembro.id,
                monto_correspondiente=Decimal("20000.00"),
            ),
        ]
    )
    session.commit()

    persisted = session.query(Gasto).one()
    suma_partes = sum(p.monto_correspondiente for p in persisted.participantes)
    assert suma_partes == persisted.importe


def test_seed_de_categorias_predefinidas_para_casa_existente():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas.upgrade(eng)

    Session = sessionmaker(bind=eng)
    db = Session()
    casa_id = uuid.uuid4()
    db.add(Casa(id=casa_id, nombre="Casa Brown"))
    db.commit()
    db.close()

    migration_gastos.upgrade(eng)

    db = Session()
    nombres = {row[0] for row in db.execute(select(Categoria.nombre).where(Categoria.casa_id == casa_id))}
    db.close()
    assert nombres == set(CATEGORIAS_PREDEFINIDAS)


def test_seed_de_categorias_es_idempotente():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas.upgrade(eng)

    Session = sessionmaker(bind=eng)
    db = Session()
    casa_id = uuid.uuid4()
    db.add(Casa(id=casa_id, nombre="Casa Brown"))
    db.commit()
    db.close()

    migration_gastos.upgrade(eng)
    migration_gastos._seed_categorias_predefinidas(eng)  # correr la siembra de nuevo

    db = Session()
    cantidad = db.query(Categoria).filter(Categoria.casa_id == casa_id).count()
    db.close()
    assert cantidad == len(CATEGORIAS_PREDEFINIDAS)
