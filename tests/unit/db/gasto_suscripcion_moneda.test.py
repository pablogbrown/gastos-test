"""T1 (spec `gastos-multi-moneda`) — `Gasto`/`Suscripcion` ganan la
columna `moneda` (`"ARS"`/`"USD"`, default `"ARS"`), vía la migración
`0010_gasto_suscripcion_moneda`.

Mismo patrón que `tests/unit/db/gasto.test.py`: SQLite en memoria,
migraciones corridas directamente por módulo (no `run_migrations`, que
se cubre aparte en `tests/integration/db/postgres_migrations.test.py`
contra Postgres real).
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.casa import Casa
from src.db.models.categoria import Categoria
from src.db.models.gasto import Gasto
from src.db.models.miembro import Miembro, RolEnum
from src.db.models.suscripcion import Suscripcion

migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")
migration_suscripciones = importlib.import_module("src.db.migrations.0009_suscripciones")
migration_moneda = importlib.import_module("src.db.migrations.0010_gasto_suscripcion_moneda")


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas.upgrade(eng)
    migration_gastos.upgrade(eng)
    migration_suscripciones.upgrade(eng)
    migration_moneda.upgrade(eng)
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


def test_migracion_0010_corre_limpia_sobre_base_vacia():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas.upgrade(eng)
    migration_gastos.upgrade(eng)
    migration_suscripciones.upgrade(eng)
    # No debe lanzar sobre una base recién creada.
    migration_moneda.upgrade(eng)


def test_migracion_0010_es_idempotente():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas.upgrade(eng)
    migration_gastos.upgrade(eng)
    migration_suscripciones.upgrade(eng)
    migration_moneda.upgrade(eng)
    # Correrla una segunda vez no debe lanzar.
    migration_moneda.upgrade(eng)


def test_gasto_sin_moneda_explicita_persiste_ars_por_default(session):
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

    persisted = session.query(Gasto).one()
    assert persisted.moneda == "ARS"


def test_gasto_con_moneda_usd_persiste_usd(session):
    casa, miembro = _crear_casa_con_miembro(session)
    categoria = Categoria(id=uuid.uuid4(), casa_id=casa.id, nombre="Supermercado")
    session.add(categoria)
    session.commit()

    gasto = Gasto(
        id=uuid.uuid4(),
        casa_id=casa.id,
        descripcion="Compra en dólares",
        importe=Decimal("20.00"),
        fecha=date(2026, 1, 1),
        pagado_por=miembro.id,
        categoria_id=categoria.id,
        moneda="USD",
    )
    session.add(gasto)
    session.commit()

    persisted = session.query(Gasto).one()
    assert persisted.moneda == "USD"


def test_suscripcion_sin_moneda_explicita_persiste_ars_por_default(session):
    casa, miembro = _crear_casa_con_miembro(session)
    categoria = Categoria(id=uuid.uuid4(), casa_id=casa.id, nombre="Streaming")
    session.add(categoria)
    session.commit()

    suscripcion = Suscripcion(
        id=uuid.uuid4(),
        casa_id=casa.id,
        descripcion="Netflix",
        importe=Decimal("5000.00"),
        categoria_id=categoria.id,
        pagado_por=miembro.id,
    )
    session.add(suscripcion)
    session.commit()

    persisted = session.query(Suscripcion).one()
    assert persisted.moneda == "ARS"


def test_suscripcion_con_moneda_usd_persiste_usd(session):
    casa, miembro = _crear_casa_con_miembro(session)
    categoria = Categoria(id=uuid.uuid4(), casa_id=casa.id, nombre="Streaming")
    session.add(categoria)
    session.commit()

    suscripcion = Suscripcion(
        id=uuid.uuid4(),
        casa_id=casa.id,
        descripcion="Netflix",
        importe=Decimal("5000.00"),
        categoria_id=categoria.id,
        pagado_por=miembro.id,
        moneda="USD",
    )
    session.add(suscripcion)
    session.commit()

    persisted = session.query(Suscripcion).one()
    assert persisted.moneda == "USD"
