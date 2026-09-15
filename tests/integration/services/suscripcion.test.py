"""T2 (spec `gastos-suscripcion-mensual`) — Servicio de suscripciones y
generación perezosa al listar gastos.

Cubre TC-001 a TC-005.
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
from src.services.exceptions import NotFoundError, PermissionDeniedError
from src.services.gasto_service import listar_gastos
from src.services.miembro_service import agregar_miembro
from src.services.suscripcion_service import (
    cancelar_suscripcion,
    crear_suscripcion,
    listar_suscripciones,
)


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
    categoria = crear_categoria(casa.id, "Servicios", admin_id)
    return casa, admin_id, categoria


def _agregar_member(db_session, casa, email="member@example.com"):
    _crear_usuario_de_prueba(db_session, email)
    admin_id = casa.miembros[0].id
    return agregar_miembro(casa.id, "Miembro", f"ID-{uuid.uuid4()}", email, admin_id)


def test_tc001_crear_suscripcion_genera_de_inmediato_el_gasto_del_mes_actual(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)

    suscripcion = crear_suscripcion(casa.id, "Netflix", Decimal("5000.00"), categoria.id, admin_id)

    assert suscripcion.activa is True
    assert suscripcion.ultimo_mes_generado is not None

    gastos = listar_gastos(casa.id)
    assert len(gastos) == 1
    assert gastos[0].importe == Decimal("5000.00")
    assert gastos[0].suscripcion_id == suscripcion.id


def test_tc002_listar_gastos_genera_el_mes_pendiente(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)
    suscripcion = crear_suscripcion(casa.id, "Gimnasio", Decimal("3000.00"), categoria.id, admin_id)

    # Simula que el último mes generado fue el mes pasado: la próxima
    # llamada a listar_gastos debe generar el gasto del mes actual.
    session = db_session()
    from src.db.models.suscripcion import Suscripcion

    s = session.get(Suscripcion, suscripcion.id)
    s.ultimo_mes_generado = "2000-01"
    session.commit()
    session.close()

    # La llamada a listar_gastos detecta que ultimo_mes_generado ("2000-01")
    # no es el mes actual y genera el gasto pendiente antes de devolver el
    # listado — ahora hay 2 gastos vinculados a esta suscripción (el del
    # alta + el recién generado).
    gastos = listar_gastos(casa.id)
    generados_por_suscripcion = [g for g in gastos if g.suscripcion_id == suscripcion.id]
    assert len(generados_por_suscripcion) == 2


def test_tc003_no_duplica_el_gasto_del_mes_ya_generado(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)
    suscripcion = crear_suscripcion(casa.id, "Gimnasio", Decimal("3000.00"), categoria.id, admin_id)

    listar_gastos(casa.id)
    listar_gastos(casa.id)

    gastos = listar_gastos(casa.id)
    generados_por_suscripcion = [g for g in gastos if g.suscripcion_id == suscripcion.id]
    assert len(generados_por_suscripcion) == 1


def test_tc004_cancelar_detiene_la_generacion_futura_sin_tocar_lo_ya_generado(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)
    suscripcion = crear_suscripcion(casa.id, "Gimnasio", Decimal("3000.00"), categoria.id, admin_id)

    gastos_antes = listar_gastos(casa.id)
    assert len(gastos_antes) == 1
    gasto_original_id = gastos_antes[0].id

    cancelada = cancelar_suscripcion(casa.id, suscripcion.id, admin_id)
    assert cancelada.activa is False

    # Simular una visita en un mes futuro: forzar ultimo_mes_generado a
    # un mes pasado no debería importar porque ya está cancelada.
    session = db_session()
    from src.db.models.suscripcion import Suscripcion

    s = session.get(Suscripcion, suscripcion.id)
    s.ultimo_mes_generado = "2000-01"
    session.commit()
    session.close()

    gastos_despues = listar_gastos(casa.id)
    generados_por_suscripcion = [g for g in gastos_despues if g.suscripcion_id == suscripcion.id]
    assert len(generados_por_suscripcion) == 1
    assert generados_por_suscripcion[0].id == gasto_original_id


def test_tc005_un_member_no_puede_crear_ni_cancelar(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)
    member = _agregar_member(db_session, casa)

    with pytest.raises(PermissionDeniedError):
        crear_suscripcion(casa.id, "Netflix", Decimal("5000.00"), categoria.id, member.id)

    suscripcion = crear_suscripcion(
        casa.id, "Netflix", Decimal("5000.00"), categoria.id, admin_id
    )

    with pytest.raises(PermissionDeniedError):
        cancelar_suscripcion(casa.id, suscripcion.id, member.id)


def test_listar_suscripciones_incluye_activas_e_inactivas(db_session):
    casa, admin_id, categoria = _armar_casa(db_session)
    activa = crear_suscripcion(casa.id, "Netflix", Decimal("5000.00"), categoria.id, admin_id)
    cancelada = crear_suscripcion(casa.id, "Spotify", Decimal("1000.00"), categoria.id, admin_id)
    cancelar_suscripcion(casa.id, cancelada.id, admin_id)

    suscripciones = listar_suscripciones(casa.id)
    assert {s.id for s in suscripciones} == {activa.id, cancelada.id}
    por_id = {s.id: s for s in suscripciones}
    assert por_id[activa.id].activa is True
    assert por_id[cancelada.id].activa is False


def test_listar_gastos_sin_ninguna_suscripcion_no_cambia_comportamiento(db_session):
    """Done When de T2: `listar_gastos` sin ninguna suscripción activa en
    la casa se comporta exactamente igual que antes."""
    casa, admin_id, categoria = _armar_casa(db_session)

    assert listar_gastos(casa.id) == []


def test_crear_suscripcion_casa_inexistente(db_session):
    with pytest.raises(NotFoundError):
        crear_suscripcion(uuid.uuid4(), "Netflix", Decimal("5000.00"), uuid.uuid4(), uuid.uuid4())
