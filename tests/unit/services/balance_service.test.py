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

from src.db.models.usuario import Usuario
from src.services.balance_service import calcular_balance, sugerir_transferencias
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.gasto_service import registrar_gasto
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


def test_balance_pablo_mas_30000_ana_menos_30000_segun_ejemplo_del_documento(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    pablo_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", pablo_id)
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, pablo_id)

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

    # Los gastos son de enero 2026 (spec `balance-mensual`: sin `mes`
    # explícito, `calcular_balance` ahora filtra por el mes calendario
    # actual, no por el mes de estos gastos de prueba).
    balance = calcular_balance(casa.id, mes="2026-01")
    por_id = {b.miembro_id: b for b in balance}

    assert por_id[pablo_id].pago == Decimal("80000.00")
    assert por_id[pablo_id].correspondia == Decimal("50000.00")
    assert por_id[pablo_id].balance == Decimal("30000.00")

    assert por_id[ana.id].pago == Decimal("20000.00")
    assert por_id[ana.id].correspondia == Decimal("50000.00")
    assert por_id[ana.id].balance == Decimal("-30000.00")


def test_transferencia_sugerida_exacta_entre_deudor_y_acreedor(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    pablo_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", pablo_id)
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, pablo_id)

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

    balance = calcular_balance(casa.id, mes="2026-01")
    transferencias = sugerir_transferencias(balance)

    assert len(transferencias) == 1
    transferencia = transferencias[0]
    assert transferencia.deudor_id == ana.id
    assert transferencia.acreedor_id == pablo_id
    assert transferencia.monto == Decimal("30000.00")


def test_sugerir_transferencias_sin_deudores_no_genera_movimientos(db_session):
    balance = calcular_balance(crear_casa("Casa Brown", uuid.uuid4()).id)
    assert sugerir_transferencias(balance) == []
