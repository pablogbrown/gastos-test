"""T1 (spec `avatares-economia`) — ledger de créditos + hook en
`completar_tarea`.

Cubre TC-001 (completar una tarea crea una `CreditoTransaccion` por el
mismo importe que los puntos) y TC-002 (recompletar una tarea ya
completada no crea créditos adicionales).
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.avatar_service import obtener_balance_creditos
from src.services.casa_service import crear_casa
from src.services.exceptions import ConflictError
from src.services.miembro_service import agregar_miembro
from src.services.tarea_service import completar_tarea, crear_tarea


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
    migracion_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migracion_tareas = importlib.import_module("src.db.migrations.0003_tareas")
    migracion_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    migracion_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    migracion_creditos = importlib.import_module("src.db.migrations.0021_creditos")
    # `completar_tarea` también dispara `logro_service.evaluar_logros`
    # (spec `gamificacion-puntos`, ya existente) — se migra/mockea acá
    # también para que este archivo no dependa del orden en que pytest
    # recolecta el resto de la suite (mismo criterio que
    # `logros.test.py`/`meta_casa.test.py`).
    migracion_gamificacion = importlib.import_module("src.db.migrations.0020_gamificacion")
    migracion_casas.upgrade(engine)
    migracion_tareas.upgrade(engine)
    migracion_actividad.upgrade(engine)
    migracion_usuarios.upgrade(engine)
    migracion_creditos.upgrade(engine)
    migracion_gamificacion.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.ranking_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.avatar_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.logro_service.get_session", lambda: TestSession())
    yield TestSession


def _casa_con_beneficiario(session_factory):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(session_factory, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
    return casa, admin_id, ana


def test_completar_tarea_otorga_creditos_por_el_mismo_importe_que_los_puntos(db_session):
    """TC-001: completar una tarea crea una `CreditoTransaccion` positiva a
    nombre del beneficiario, por el mismo importe que sus
    `puntos_obtenidos`."""
    casa, admin_id, ana = _casa_con_beneficiario(db_session)
    tarea = crear_tarea(casa.id, "Sacar la basura", 15, actor=admin_id)

    assert obtener_balance_creditos(ana.id) == 0

    completar_tarea(tarea.id, ana.id, ana.id)

    assert obtener_balance_creditos(ana.id) == 15


def test_completar_tarea_en_nombre_de_otro_otorga_creditos_al_beneficiario_no_al_actor(db_session):
    """Un Administrador completando en nombre de otro miembro nunca recibe
    él mismo los créditos — el beneficiario es quien se acredita."""
    casa, admin_id, ana = _casa_con_beneficiario(db_session)
    tarea = crear_tarea(casa.id, "Sacar la basura", 10, actor=admin_id)

    completar_tarea(tarea.id, ana.id, admin_id)

    assert obtener_balance_creditos(ana.id) == 10
    assert obtener_balance_creditos(admin_id) == 0


def test_recompletar_una_tarea_no_otorga_creditos_adicionales(db_session):
    """TC-002: recompletar una tarea ya completada no crea ninguna
    `CreditoTransaccion` adicional, igual que hoy no se otorgan puntos
    adicionales."""
    casa, admin_id, ana = _casa_con_beneficiario(db_session)
    tarea = crear_tarea(casa.id, "Sacar la basura", 15, actor=admin_id)

    completar_tarea(tarea.id, ana.id, ana.id)
    assert obtener_balance_creditos(ana.id) == 15

    with pytest.raises(ConflictError):
        completar_tarea(tarea.id, ana.id, ana.id)

    assert obtener_balance_creditos(ana.id) == 15
