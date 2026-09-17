"""T2 (spec `gastos-multi-moneda`/`gastos-sin-reparto`) —
`calcular_balance` separa `totales`/`aportes` por moneda, nunca sumados
ni convertidos entre sí.

Cubre TC-003, TC-004 y TC-005.
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
from src.services.balance_service import calcular_balance
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.gasto_service import GastoMetadata, registrar_gasto
from src.services.miembro_service import agregar_miembro


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
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.balance_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    yield TestSession


def _armar_casa_con_dos_miembros(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    pablo_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", pablo_id)
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, pablo_id)
    return casa, pablo_id, ana.id, categoria


def test_tc003_totales_separados_por_moneda_con_actividad_en_ambas(db_session):
    casa, pablo_id, ana_id, categoria = _armar_casa_con_dos_miembros(db_session)

    registrar_gasto(
        casa.id,
        "Super en pesos",
        Decimal("50000.00"),
        date(2026, 1, 1),
        categoria.id,
        pablo_id,
        pablo_id,
    )
    registrar_gasto(
        casa.id,
        "Compra en dólares",
        Decimal("20.00"),
        date(2026, 1, 2),
        categoria.id,
        pablo_id,
        pablo_id,
        metadata=GastoMetadata(moneda="USD"),
    )

    balance = calcular_balance(casa.id, mes="2026-01")
    totales_por_moneda = {t.moneda: t.total_gastos for t in balance.totales}

    assert totales_por_moneda["ARS"] == Decimal("50000.00")
    assert totales_por_moneda["USD"] == Decimal("20.00")
    # Ninguna fila de una moneda contamina el total de la otra.
    assert totales_por_moneda["ARS"] != totales_por_moneda["USD"]


def test_tc004_aportes_separados_por_moneda_con_actividad_en_ambas(db_session):
    casa, pablo_id, ana_id, categoria = _armar_casa_con_dos_miembros(db_session)

    registrar_gasto(
        casa.id,
        "Super en pesos",
        Decimal("50000.00"),
        date(2026, 1, 1),
        categoria.id,
        pablo_id,
        pablo_id,
    )
    registrar_gasto(
        casa.id,
        "Compra en dólares",
        Decimal("20.00"),
        date(2026, 1, 2),
        categoria.id,
        ana_id,
        ana_id,
        metadata=GastoMetadata(moneda="USD"),
    )

    balance = calcular_balance(casa.id, mes="2026-01")
    aportes_ars = {a.miembro_id: a for a in balance.aportes if a.moneda == "ARS"}
    aportes_usd = {a.miembro_id: a for a in balance.aportes if a.moneda == "USD"}

    # ARS: comportamiento actual sin cambios — una fila por cada miembro,
    # incluso en 0.
    assert aportes_ars[pablo_id].total == Decimal("50000.00")
    assert aportes_ars[ana_id].total == Decimal("0")

    # USD: solo actividad real, nunca mezclada con las filas ARS.
    assert set(aportes_usd) == {ana_id}
    assert aportes_usd[ana_id].total == Decimal("20.00")


def test_tc004_sin_actividad_en_usd_no_hay_ninguna_fila_usd(db_session):
    casa, pablo_id, ana_id, categoria = _armar_casa_con_dos_miembros(db_session)

    registrar_gasto(
        casa.id,
        "Super en pesos",
        Decimal("10000.00"),
        date(2026, 1, 1),
        categoria.id,
        pablo_id,
        pablo_id,
    )

    balance = calcular_balance(casa.id, mes="2026-01")

    assert all(t.moneda == "ARS" for t in balance.totales)
    assert all(a.moneda == "ARS" for a in balance.aportes)
    # ARS sigue mostrando a todos los miembros, incluso en 0 (control,
    # comportamiento preexistente sin cambios).
    assert {a.miembro_id for a in balance.aportes} == {pablo_id, ana_id}


def test_tc005_balance_sin_actividad_no_expone_ninguna_transferencia(db_session):
    """Control (spec `gastos-sin-reparto`): sin reparto no hay ninguna
    deuda que sugerir saldar — `BalanceCasa` no expone ningún campo de
    transferencia, con o sin actividad."""
    casa, _pablo_id, _ana_id, _categoria = _armar_casa_con_dos_miembros(db_session)
    balance = calcular_balance(casa.id, mes="2026-01")

    assert not hasattr(balance, "transferencias")
    assert set(balance.__dataclass_fields__.keys()) == {"totales", "aportes"}
