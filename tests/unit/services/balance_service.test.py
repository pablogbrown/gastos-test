"""T2 — Service Layer (unit slice): calcular_balance y sugerir_transferencias.

Cubre TC-007 y TC-008.
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.services.balance_service import calcular_balance, sugerir_transferencias
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.gasto_service import registrar_gasto
from src.services.miembro_service import agregar_miembro


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.balance_service.get_session", lambda: TestSession())
    yield TestSession


def test_balance_pablo_mas_30000_ana_menos_30000_segun_ejemplo_del_documento(db_session):
    pablo_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", pablo_id)
    categoria = crear_categoria(casa.id, "Supermercado", pablo_id)
    ana = agregar_miembro(casa.id, "Ana", "ANA1", pablo_id)

    # Pablo pagó $80.000, Ana pagó $20.000; a cada uno le correspondía $50.000.
    registrar_gasto(
        casa.id,
        "Gasto de Pablo",
        Decimal("80000.00"),
        date(2026, 1, 1),
        categoria.id,
        pablo_id,
        pablo_id,
        participantes=[pablo_id, ana.id],
    )
    registrar_gasto(
        casa.id,
        "Gasto de Ana",
        Decimal("20000.00"),
        date(2026, 1, 2),
        categoria.id,
        ana.id,
        ana.id,
        participantes=[pablo_id, ana.id],
    )

    balance = calcular_balance(casa.id)
    por_id = {b.miembro_id: b for b in balance}

    assert por_id[pablo_id].pago == Decimal("80000.00")
    assert por_id[pablo_id].correspondia == Decimal("50000.00")
    assert por_id[pablo_id].balance == Decimal("30000.00")

    assert por_id[ana.id].pago == Decimal("20000.00")
    assert por_id[ana.id].correspondia == Decimal("50000.00")
    assert por_id[ana.id].balance == Decimal("-30000.00")


def test_transferencia_sugerida_exacta_entre_deudor_y_acreedor(db_session):
    pablo_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", pablo_id)
    categoria = crear_categoria(casa.id, "Supermercado", pablo_id)
    ana = agregar_miembro(casa.id, "Ana", "ANA1", pablo_id)

    registrar_gasto(
        casa.id,
        "Gasto de Pablo",
        Decimal("80000.00"),
        date(2026, 1, 1),
        categoria.id,
        pablo_id,
        pablo_id,
        participantes=[pablo_id, ana.id],
    )
    registrar_gasto(
        casa.id,
        "Gasto de Ana",
        Decimal("20000.00"),
        date(2026, 1, 2),
        categoria.id,
        ana.id,
        ana.id,
        participantes=[pablo_id, ana.id],
    )

    balance = calcular_balance(casa.id)
    transferencias = sugerir_transferencias(balance)

    assert len(transferencias) == 1
    transferencia = transferencias[0]
    assert transferencia.deudor_id == ana.id
    assert transferencia.acreedor_id == pablo_id
    assert transferencia.monto == Decimal("30000.00")


def test_sugerir_transferencias_sin_deudores_no_genera_movimientos(db_session):
    balance = calcular_balance(crear_casa("Casa Brown", uuid.uuid4()).id)
    assert sugerir_transferencias(balance) == []
