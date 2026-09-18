"""T3 (spec `gamificacion-puntos`) — meta de puntos mensual de la casa.

Cubre TC-006: un Administrador puede configurar la meta; un miembro
no-admin no puede. El progreso mostrado (suma de puntos de todos los
miembros ese mes) coincide con lo esperado.
"""
import importlib
import uuid
from datetime import date, datetime, time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.historial_tarea import HistorialTarea
from src.db.models.usuario import Usuario
from src.services.casa_service import actualizar_meta_puntos, crear_casa
from src.services.exceptions import PermissionDeniedError, ValidationError
from src.services.miembro_service import agregar_miembro
from src.services.ranking_service import calcular_progreso_meta
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
    migracion_gamificacion = importlib.import_module("src.db.migrations.0020_gamificacion")
    migracion_casas.upgrade(engine)
    migracion_tareas.upgrade(engine)
    migracion_actividad.upgrade(engine)
    migracion_usuarios.upgrade(engine)
    migracion_gamificacion.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.ranking_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.logro_service.get_session", lambda: TestSession())
    yield TestSession


def _completar_en_fecha(session_factory, tarea_id, miembro_id, actor_id, fecha: date):
    historial = completar_tarea(tarea_id, miembro_id, actor_id)
    session = session_factory()
    try:
        fila = session.get(HistorialTarea, historial.id)
        fila.completada_en = datetime.combine(fecha, time(12, 0))
        session.commit()
    finally:
        session.close()
    return historial


def test_un_administrador_puede_configurar_la_meta(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id

    casa_actualizada = actualizar_meta_puntos(casa.id, 100, admin_id)

    assert casa_actualizada.meta_puntos_mensual == 100


def test_un_no_admin_no_puede_configurar_la_meta(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    with pytest.raises(PermissionDeniedError):
        actualizar_meta_puntos(casa.id, 100, ana.id)


def test_meta_none_desactiva_la_meta(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id

    actualizar_meta_puntos(casa.id, 100, admin_id)
    casa_actualizada = actualizar_meta_puntos(casa.id, None, admin_id)

    assert casa_actualizada.meta_puntos_mensual is None


def test_meta_negativa_es_rechazada(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id

    with pytest.raises(ValidationError):
        actualizar_meta_puntos(casa.id, -5, admin_id)


def test_calcular_progreso_meta_es_none_sin_meta_configurada(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)

    assert calcular_progreso_meta(casa.id, "2026-09") is None


def test_calcular_progreso_meta_suma_todos_los_miembros_del_mes(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    actualizar_meta_puntos(casa.id, 100, admin_id)

    tarea_admin = crear_tarea(casa.id, "Tarea admin", 30, actor=admin_id)
    _completar_en_fecha(db_session, tarea_admin.id, admin_id, admin_id, date(2026, 9, 5))
    tarea_ana = crear_tarea(casa.id, "Tarea Ana", 20, actor=admin_id)
    _completar_en_fecha(db_session, tarea_ana.id, ana.id, ana.id, date(2026, 9, 10))
    # Tarea de un mes distinto: no debe contar en el progreso de septiembre.
    tarea_agosto = crear_tarea(casa.id, "Tarea de agosto", 999, actor=admin_id)
    _completar_en_fecha(db_session, tarea_agosto.id, ana.id, ana.id, date(2026, 8, 1))

    progreso = calcular_progreso_meta(casa.id, "2026-09")

    assert progreso == {"puntos_acumulados": 50, "meta": 100, "porcentaje": 50.0}
