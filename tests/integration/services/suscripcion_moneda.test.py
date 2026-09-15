"""T2 (spec `gastos-multi-moneda`) — `crear_suscripcion` valida y
persiste `moneda`; `generar_gastos_pendientes` copia la moneda de la
suscripción a cada gasto generado.

Cubre TC-006.
"""
import importlib
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.exceptions import ValidationError
from src.services.gasto_service import listar_gastos
from src.services.suscripcion_service import crear_suscripcion, generar_gastos_pendientes


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
    categoria = crear_categoria(casa.id, "Streaming", admin_id)
    return casa, admin_id, categoria


def test_tc006_suscripcion_en_usd_genera_el_gasto_del_mes_en_usd(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    suscripcion = crear_suscripcion(
        casa.id, "Netflix", Decimal("15.00"), categoria.id, admin_id, moneda="USD"
    )

    assert suscripcion.moneda == "USD"
    (gasto_generado,) = listar_gastos(casa.id)
    assert gasto_generado.moneda == "USD"
    assert gasto_generado.suscripcion_id == suscripcion.id


def test_suscripcion_sin_moneda_persiste_ars_por_default(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    suscripcion = crear_suscripcion(casa.id, "Netflix", Decimal("5000.00"), categoria.id, admin_id)

    assert suscripcion.moneda == "ARS"
    (gasto_generado,) = listar_gastos(casa.id)
    assert gasto_generado.moneda == "ARS"


def test_moneda_invalida_en_suscripcion_es_rechazada(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    with pytest.raises(ValidationError):
        crear_suscripcion(
            casa.id, "Netflix", Decimal("15.00"), categoria.id, admin_id, moneda="EUR"
        )


def test_generar_gastos_pendientes_copia_la_moneda_de_la_suscripcion(db_session, monkeypatch):
    """`generar_gastos_pendientes` (disparado por una segunda visita en un
    mes distinto) debe seguir copiando `moneda` — no solo la primera
    generación inmediata de `crear_suscripcion`."""
    casa, admin_id, categoria = _armar_casa(db_session)
    suscripcion = crear_suscripcion(
        casa.id, "Netflix", Decimal("15.00"), categoria.id, admin_id, moneda="USD"
    )

    # Simula que la suscripción no generó nada este mes todavía, para
    # forzar el camino de `generar_gastos_pendientes` (no solo la
    # generación inmediata de `crear_suscripcion`).
    session = db_session()
    try:
        from src.db.models.suscripcion import Suscripcion

        s = session.get(Suscripcion, suscripcion.id)
        s.ultimo_mes_generado = None
        session.commit()
    finally:
        session.close()

    generar_gastos_pendientes(casa.id)

    gastos = listar_gastos(casa.id)
    assert len(gastos) >= 1
    assert all(g.moneda == "USD" for g in gastos)
