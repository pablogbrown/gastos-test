"""T2 (spec `gastos-multi-moneda`) — `registrar_gasto` valida y persiste
`moneda`; `_crear_gastos_en_cuotas` propaga la misma moneda a cada cuota.

Cubre TC-001, TC-002 (control) y TC-007.
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.exceptions import ValidationError
from src.services.gasto_service import GastoMetadata, listar_gastos, registrar_gasto


def _crear_usuario_de_prueba(session_factory, email):
    session = session_factory()
    try:
        usuario = Usuario(id=uuid.uuid4(), email=email, password_hash="hash-de-prueba")
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario
    finally:
        session.close()


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    migration_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    migration_suscripciones = importlib.import_module("src.db.migrations.0009_suscripciones")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)
    migration_suscripciones.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.suscripcion_service.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", admin_id)
    return casa, admin_id, categoria


def test_tc001_gasto_con_moneda_usd_persiste_usd(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    gasto = registrar_gasto(
        casa.id,
        "Compra en dólares",
        Decimal("20.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
        metadata=GastoMetadata(moneda="USD"),
    )

    assert gasto.moneda == "USD"
    (persistido,) = listar_gastos(casa.id)
    assert persistido.moneda == "USD"


def test_tc002_gasto_sin_moneda_persiste_ars_por_default(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    gasto = registrar_gasto(
        casa.id,
        "Compra semanal",
        Decimal("20000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )

    assert gasto.moneda == "ARS"


def test_tc007_las_3_cuotas_mantienen_la_misma_moneda_usd(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    registrar_gasto(
        casa.id,
        "Heladera",
        Decimal("300.00"),
        date(2026, 9, 15),
        categoria.id,
        admin_id,
        admin_id,
        metadata=GastoMetadata(cuotas=3, moneda="USD"),
    )

    gastos = sorted(listar_gastos(casa.id), key=lambda g: g.cuota_numero)
    assert len(gastos) == 3
    assert all(g.moneda == "USD" for g in gastos)


def test_moneda_invalida_es_rechazada_con_validation_error(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    with pytest.raises(ValidationError):
        registrar_gasto(
            casa.id,
            "Compra",
            Decimal("100.00"),
            date(2026, 1, 1),
            categoria.id,
            admin_id,
            admin_id,
            metadata=GastoMetadata(moneda="EUR"),
        )

    assert listar_gastos(casa.id) == []
