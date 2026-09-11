"""T2 — Service Layer (integration slice): estabilidad de gastos ya
registrados frente a cambios en la membresía de la casa.

Cubre TC-009.
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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
    # 0004 (spec `dashboard-actividad`): `registrar_gasto` dispara un hook
    # a `actividad_service.registrar_actividad`, que requiere la tabla
    # `historial_actividad`.
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    yield TestSession


def test_nuevo_miembro_no_altera_gastos_ya_registrados(db_session):
    admin_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", admin_id)
    categoria = crear_categoria(casa.id, "Supermercado", admin_id)
    ana = agregar_miembro(casa.id, "Ana", "ANA1", admin_id)

    gasto = registrar_gasto(
        casa.id,
        "Compra semanal",
        Decimal("20000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )
    ids_participantes_originales = {p.miembro_id for p in gasto.participantes}
    montos_originales = {p.miembro_id: p.monto_correspondiente for p in gasto.participantes}

    assert ids_participantes_originales == {admin_id, ana.id}

    # Se agrega un tercer miembro a la casa DESPUÉS del registro del gasto.
    agregar_miembro(casa.id, "Bruno", "BRU1", admin_id)

    from src.services.gasto_service import listar_gastos

    (gasto_persistido,) = listar_gastos(casa.id)
    ids_participantes_actuales = {p.miembro_id for p in gasto_persistido.participantes}
    montos_actuales = {p.miembro_id: p.monto_correspondiente for p in gasto_persistido.participantes}

    assert ids_participantes_actuales == ids_participantes_originales
    assert montos_actuales == montos_originales
    assert gasto_persistido.importe == Decimal("20000.00")
