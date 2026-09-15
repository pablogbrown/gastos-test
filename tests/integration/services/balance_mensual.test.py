"""T1 (spec `balance-mensual`) — `calcular_balance` filtra por mes.

Cubre TC-001 (sin mes explícito usa el mes actual), TC-002 (con mes
explícito filtra correctamente) y TC-003 (mes con formato inválido es
rechazado) a nivel de servicio. TC-003 se re-verifica a nivel HTTP (400)
en `tests/integration/api/gastos_routes.test.py` (T2).
"""
import importlib
import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.balance_service import calcular_balance
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.exceptions import ValidationError
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
    migration_tareas = importlib.import_module("src.db.migrations.0003_tareas")
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    migration_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    # 0009 (spec `gastos-suscripcion-mensual`): `gasto_service.listar_gastos`
    # (llamado indirectamente por `dashboard_service.armar_dashboard`) ahora
    # dispara `suscripcion_service.generar_gastos_pendientes` como primera
    # línea, que requiere la tabla `suscripciones`.
    migration_suscripciones = importlib.import_module("src.db.migrations.0009_suscripciones")
    # 0011 (spec `tarjetas-credito`): `armar_dashboard` ahora llama a
    # `obtener_tarjetas_con_alerta`, que requiere la tabla
    # `tarjetas_credito`.
    migration_tarjetas = importlib.import_module("src.db.migrations.0011_tarjetas_credito")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_tareas.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)
    migration_suscripciones.upgrade(engine)
    migration_tarjetas.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.balance_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.ranking_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.suscripcion_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarjeta_service.get_session", lambda: TestSession())
    yield TestSession


def _mes_anterior(hoy: date) -> date:
    primer_dia_mes_actual = hoy.replace(day=1)
    return primer_dia_mes_actual - timedelta(days=1)


def test_sin_mes_usa_el_mes_actual(db_session):
    """TC-001: un gasto de este mes y otro de un mes anterior — sin
    indicar `mes`, solo el de este mes está reflejado."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    pablo_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", pablo_id)

    hoy = date.today()
    mes_pasado = _mes_anterior(hoy)

    registrar_gasto(
        casa.id, "Gasto de este mes", Decimal("100.00"), hoy, categoria.id, pablo_id, pablo_id,
        participantes=[pablo_id],
    )
    registrar_gasto(
        casa.id, "Gasto de mes anterior", Decimal("500.00"), mes_pasado, categoria.id, pablo_id, pablo_id,
        participantes=[pablo_id],
    )

    balance = calcular_balance(casa.id)
    por_id = {b.miembro_id: b for b in balance}
    assert por_id[pablo_id].pago == Decimal("100.00")
    assert por_id[pablo_id].correspondia == Decimal("100.00")


def test_con_mes_explicito_filtra_correctamente(db_session):
    """TC-002: gastos en agosto y septiembre de 2026 — `mes=2026-08` solo
    refleja el gasto de agosto."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    pablo_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", pablo_id)

    registrar_gasto(
        casa.id, "Gasto de agosto", Decimal("200.00"), date(2026, 8, 15), categoria.id, pablo_id, pablo_id,
        participantes=[pablo_id],
    )
    registrar_gasto(
        casa.id, "Gasto de septiembre", Decimal("300.00"), date(2026, 9, 1), categoria.id, pablo_id, pablo_id,
        participantes=[pablo_id],
    )

    balance_agosto = calcular_balance(casa.id, mes="2026-08")
    por_id = {b.miembro_id: b for b in balance_agosto}
    assert por_id[pablo_id].pago == Decimal("200.00")
    assert por_id[pablo_id].correspondia == Decimal("200.00")

    balance_septiembre = calcular_balance(casa.id, mes="2026-09")
    por_id_sep = {b.miembro_id: b for b in balance_septiembre}
    assert por_id_sep[pablo_id].pago == Decimal("300.00")


def test_mes_con_formato_invalido_lanza_validation_error(db_session):
    """TC-003 (a nivel de servicio; T2 re-verifica como 400 HTTP)."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)

    with pytest.raises(ValidationError):
        calcular_balance(casa.id, mes="fecha-invalida")


def test_mes_con_numero_de_mes_fuera_de_rango_lanza_validation_error(db_session):
    """`"2026-13"` pasa el `int()` pero no es un mes válido (Failure
    Triage, 10-verify.md)."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)

    with pytest.raises(ValidationError):
        calcular_balance(casa.id, mes="2026-13")


def test_dashboard_service_no_rompe_con_el_nuevo_default(db_session):
    """`dashboard_service.armar_dashboard` sigue llamando a
    `calcular_balance(casa_id)` sin `mes` — hereda el nuevo default (mes
    actual) automáticamente, sin romper (00-overview.md, Arquitectura)."""
    from src.services.dashboard_service import armar_dashboard

    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    dashboard = armar_dashboard(casa.id)
    assert all(b.pago == Decimal("0") and b.correspondia == Decimal("0") for b in dashboard.balance)
