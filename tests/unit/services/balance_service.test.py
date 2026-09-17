"""T2 (spec `gastos-sin-reparto`) — Service Layer (unit slice):
`calcular_balance` devuelve el total gastado de la casa por moneda
(`totales`) y el aporte informativo de cada miembro (`aportes`), sin
ningún campo de deuda ni transferencia sugerida.

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
from src.services.balance_service import BalanceCasa, calcular_balance
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.gasto_service import GastoMetadata, registrar_gasto
from src.services.miembro_service import agregar_miembro


def _crear_usuario_de_prueba(session_factory, email):
    """Inserta un Usuario real (spec `usuarios-auth`): `agregar_miembro`
    ahora exige que el email vinculado ya exista."""
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
    # 0004 (spec `dashboard-actividad`): `registrar_gasto` dispara un hook
    # a `actividad_service.registrar_actividad`, que requiere la tabla
    # `historial_actividad`.
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email) para vincular al nuevo Miembro.
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


def test_tc003_total_gastado_de_la_casa_por_moneda(db_session):
    casa, pablo_id, ana_id, categoria = _armar_casa_con_dos_miembros(db_session)

    registrar_gasto(
        casa.id, "Super en pesos", Decimal("50000.00"), date(2026, 1, 1), categoria.id,
        pablo_id, pablo_id,
    )
    registrar_gasto(
        casa.id, "Otro gasto en pesos", Decimal("30000.00"), date(2026, 1, 2), categoria.id,
        ana_id, ana_id,
    )
    registrar_gasto(
        casa.id, "Compra en dólares", Decimal("20.00"), date(2026, 1, 3), categoria.id,
        pablo_id, pablo_id, metadata=GastoMetadata(moneda="USD"),
    )

    balance = calcular_balance(casa.id, mes="2026-01")
    totales_por_moneda = {t.moneda: t.total_gastos for t in balance.totales}

    assert totales_por_moneda["ARS"] == Decimal("80000.00")
    assert totales_por_moneda["USD"] == Decimal("20.00")


def test_tc003_ars_siempre_presente_incluso_sin_actividad(db_session):
    casa, _pablo_id, _ana_id, _categoria = _armar_casa_con_dos_miembros(db_session)

    balance = calcular_balance(casa.id, mes="2026-01")
    monedas = {t.moneda for t in balance.totales}

    assert "ARS" in monedas
    assert "USD" not in monedas
    total_ars = next(t for t in balance.totales if t.moneda == "ARS")
    assert total_ars.total_gastos == Decimal("0")


def test_tc004_aporte_por_miembro_sin_ningun_campo_de_deuda(db_session):
    casa, pablo_id, ana_id, categoria = _armar_casa_con_dos_miembros(db_session)

    registrar_gasto(
        casa.id, "Gasto de Pablo", Decimal("80000.00"), date(2026, 1, 1), categoria.id,
        pablo_id, pablo_id,
    )
    registrar_gasto(
        casa.id, "Gasto de Ana", Decimal("20000.00"), date(2026, 1, 2), categoria.id,
        ana_id, ana_id,
    )

    balance = calcular_balance(casa.id, mes="2026-01")
    aportes_por_id = {a.miembro_id: a for a in balance.aportes}

    assert aportes_por_id[pablo_id].total == Decimal("80000.00")
    assert aportes_por_id[pablo_id].nombre == "Administrador"
    assert aportes_por_id[ana_id].total == Decimal("20000.00")

    # Ningún dataclass expone "correspondía"/"balance" — solo `total`.
    for aporte in balance.aportes:
        assert not hasattr(aporte, "correspondia")
        assert not hasattr(aporte, "balance")
        assert not hasattr(aporte, "pago")


def test_tc004_aporte_incluye_todo_miembro_de_la_casa_incluso_en_cero(db_session):
    casa, pablo_id, ana_id, categoria = _armar_casa_con_dos_miembros(db_session)

    registrar_gasto(
        casa.id, "Solo Pablo gasta", Decimal("10000.00"), date(2026, 1, 1), categoria.id,
        pablo_id, pablo_id,
    )

    balance = calcular_balance(casa.id, mes="2026-01")
    aportes_por_id = {a.miembro_id: a for a in balance.aportes}

    assert aportes_por_id[pablo_id].total == Decimal("10000.00")
    assert aportes_por_id[ana_id].total == Decimal("0")


def test_tc005_balance_casa_no_expone_ninguna_transferencia(db_session):
    """Control (REQ-004): `BalanceCasa` — y el módulo `balance_service`
    en su conjunto — no exponen ningún concepto de transferencia
    sugerida ni de deuda entre miembros."""
    import src.services.balance_service as balance_service_module

    assert not hasattr(balance_service_module, "sugerir_transferencias")
    assert not hasattr(balance_service_module, "Transferencia")
    assert not hasattr(balance_service_module, "BalancePorMiembro")

    campos_balance_casa = BalanceCasa.__dataclass_fields__.keys()
    assert set(campos_balance_casa) == {"totales", "aportes"}
