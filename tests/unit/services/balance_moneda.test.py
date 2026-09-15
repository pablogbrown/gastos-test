"""T2 (spec `gastos-multi-moneda`) — `calcular_balance` agrupa por
(miembro, moneda); `sugerir_transferencias` nunca cruza monedas.

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
from src.services.balance_service import calcular_balance, sugerir_transferencias
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.gasto_service import registrar_gasto
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


def test_tc003_balance_separado_por_moneda_con_actividad_en_ambas(db_session):
    casa, pablo_id, ana_id, categoria = _armar_casa_con_dos_miembros(db_session)

    registrar_gasto(
        casa.id,
        "Super en pesos",
        Decimal("50000.00"),
        date(2026, 1, 1),
        categoria.id,
        pablo_id,
        pablo_id,
        participantes=[pablo_id, ana_id],
    )
    registrar_gasto(
        casa.id,
        "Compra en dólares",
        Decimal("20.00"),
        date(2026, 1, 2),
        categoria.id,
        pablo_id,
        pablo_id,
        participantes=[pablo_id, ana_id],
        moneda="USD",
    )

    balance = calcular_balance(casa.id, mes="2026-01")
    filas_ars = [b for b in balance if b.moneda == "ARS"]
    filas_usd = [b for b in balance if b.moneda == "USD"]

    # ARS: comportamiento actual sin cambios — una fila por cada miembro.
    assert {b.miembro_id for b in filas_ars} == {pablo_id, ana_id}
    pablo_ars = next(b for b in filas_ars if b.miembro_id == pablo_id)
    assert pablo_ars.pago == Decimal("50000.00")
    assert pablo_ars.correspondia == Decimal("25000.00")

    # USD: solo actividad real, nunca mezclada con las filas ARS.
    assert {b.miembro_id for b in filas_usd} == {pablo_id, ana_id}
    pablo_usd = next(b for b in filas_usd if b.miembro_id == pablo_id)
    assert pablo_usd.pago == Decimal("20.00")
    assert pablo_usd.correspondia == Decimal("10.00")

    # Ninguna fila de una moneda contamina el total de la otra.
    assert pablo_ars.pago != pablo_usd.pago


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
        participantes=[pablo_id, ana_id],
    )

    balance = calcular_balance(casa.id, mes="2026-01")

    assert all(b.moneda == "ARS" for b in balance)
    # ARS sigue mostrando a todos los miembros, incluso en 0 (control,
    # comportamiento preexistente sin cambios).
    assert {b.miembro_id for b in balance} == {pablo_id, ana_id}


def test_tc005_transferencias_sugeridas_nunca_cruzan_moneda(db_session):
    casa, pablo_id, ana_id, categoria = _armar_casa_con_dos_miembros(db_session)

    # Pablo paga todo en ARS (Ana le debe en ARS); Ana paga todo en USD
    # (Pablo le debe en USD) — si el algoritmo cruzara monedas, emparejaría
    # a Pablo (acreedor ARS) con... nada compatible, o peor, generaría una
    # transferencia mezclando ambas.
    registrar_gasto(
        casa.id,
        "Super en pesos",
        Decimal("40000.00"),
        date(2026, 1, 1),
        categoria.id,
        pablo_id,
        pablo_id,
        participantes=[pablo_id, ana_id],
    )
    registrar_gasto(
        casa.id,
        "Compra en dólares",
        Decimal("40.00"),
        date(2026, 1, 2),
        categoria.id,
        ana_id,
        ana_id,
        participantes=[pablo_id, ana_id],
        moneda="USD",
    )

    balance = calcular_balance(casa.id, mes="2026-01")
    transferencias = sugerir_transferencias(balance)

    assert len(transferencias) == 2
    monedas = {t.moneda for t in transferencias}
    assert monedas == {"ARS", "USD"}

    transferencia_ars = next(t for t in transferencias if t.moneda == "ARS")
    assert transferencia_ars.deudor_id == ana_id
    assert transferencia_ars.acreedor_id == pablo_id
    assert transferencia_ars.monto == Decimal("20000.00")

    transferencia_usd = next(t for t in transferencias if t.moneda == "USD")
    assert transferencia_usd.deudor_id == pablo_id
    assert transferencia_usd.acreedor_id == ana_id
    assert transferencia_usd.monto == Decimal("20.00")


def test_sugerir_transferencias_sin_actividad_no_genera_movimientos(db_session):
    casa, _pablo_id, _ana_id, _categoria = _armar_casa_con_dos_miembros(db_session)
    balance = calcular_balance(casa.id, mes="2026-01")
    assert sugerir_transferencias(balance) == []
