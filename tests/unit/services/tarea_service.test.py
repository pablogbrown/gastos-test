"""T2 — Service Layer (unit slice): tarea_service.

Cubre TC-001, TC-002, TC-004, TC-005, TC-006 y TC-009.
"""
import importlib
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.tarea import EstadoTareaEnum
from src.db.models.usuario import Usuario
from src.services.casa_service import crear_casa
from src.services.exceptions import (
    ConflictError,
    PermissionDeniedError,
    ValidationError,
)
from src.services.miembro_service import agregar_miembro
from src.services.tarea_service import completar_tarea, crear_tarea, procesar_recurrencia


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
    migracion_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migracion_tareas = importlib.import_module("src.db.migrations.0003_tareas")
    # 0004 (spec `dashboard-actividad`): `crear_tarea`/`completar_tarea`
    # disparan un hook a `actividad_service.registrar_actividad`, que
    # requiere la tabla `historial_actividad`.
    migracion_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email) para vincular al nuevo Miembro.
    migracion_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    migracion_casas.upgrade(engine)
    migracion_tareas.upgrade(engine)
    migracion_actividad.upgrade(engine)
    migracion_usuarios.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    yield TestSession


def _casa_con_admin_y_miembro(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    # Spec `usuarios-auth`: `Miembro.id` ya no es el `usuario_id` del
    # creador (ver Design Rationale de `crear_casa`) — el actor que usan
    # los demás servicios de esta casa es el `Miembro.id` del admin.
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
    return casa, admin_id, ana


def test_crear_tarea_con_nombre_y_puntos_validos(db_session):
    casa, admin_id, _ = _casa_con_admin_y_miembro(db_session)

    tarea = crear_tarea(casa.id, "Lavar los platos", 5, actor=admin_id)

    assert tarea.nombre == "Lavar los platos"
    assert tarea.puntos == 5
    assert tarea.estado == EstadoTareaEnum.PENDIENTE


def test_crear_tarea_sin_nombre_es_rechazada(db_session):
    casa, admin_id, _ = _casa_con_admin_y_miembro(db_session)

    with pytest.raises(ValidationError):
        crear_tarea(casa.id, "", 5, actor=admin_id)
    with pytest.raises(ValidationError):
        crear_tarea(casa.id, "   ", 5, actor=admin_id)


def test_crear_tarea_sin_puntos_es_rechazada(db_session):
    casa, admin_id, _ = _casa_con_admin_y_miembro(db_session)

    with pytest.raises(ValidationError):
        crear_tarea(casa.id, "Lavar los platos", None, actor=admin_id)


def test_crear_tarea_sin_actor_miembro_activo_es_rechazada(db_session):
    casa, _admin_id, _ = _casa_con_admin_y_miembro(db_session)
    ajeno = uuid.uuid4()

    with pytest.raises(PermissionDeniedError):
        crear_tarea(casa.id, "Lavar los platos", 5, actor=ajeno)


def test_crear_tarea_recurrente_sin_frecuencia_es_rechazada(db_session):
    casa, admin_id, _ = _casa_con_admin_y_miembro(db_session)

    with pytest.raises(ValidationError):
        crear_tarea(casa.id, "Sacar la basura", 3, actor=admin_id, recurrente=True)


def test_tarea_sin_responsable_puede_completarla_cualquier_miembro_activo(db_session):
    casa, admin_id, ana = _casa_con_admin_y_miembro(db_session)
    tarea = crear_tarea(casa.id, "Sacar la basura", 5, actor=admin_id)

    historial = completar_tarea(tarea.id, ana.id, ana.id)

    assert historial.miembro_id == ana.id
    assert historial.puntos_obtenidos == 5


def test_completar_tarea_registra_quien_cuando_y_otorga_puntos(db_session):
    casa, admin_id, ana = _casa_con_admin_y_miembro(db_session)
    tarea = crear_tarea(casa.id, "Limpiar el baño", 10, actor=admin_id)

    historial = completar_tarea(tarea.id, ana.id, ana.id)

    assert historial.tarea_id == tarea.id
    assert historial.miembro_id == ana.id
    assert historial.puntos_obtenidos == 10
    assert historial.completada_en is not None


def test_completar_tarea_ya_completada_es_rechazada_sin_puntos_adicionales(db_session):
    casa, admin_id, ana = _casa_con_admin_y_miembro(db_session)
    tarea = crear_tarea(casa.id, "Sacar la basura", 5, actor=admin_id)
    completar_tarea(tarea.id, ana.id, ana.id)

    with pytest.raises(ConflictError):
        completar_tarea(tarea.id, ana.id, ana.id)


def test_solo_el_responsable_asignado_o_un_admin_puede_completar_la_tarea(db_session):
    casa, admin_id, ana = _casa_con_admin_y_miembro(db_session)
    bruno_usuario = _crear_usuario_de_prueba(db_session, "bruno@example.com")
    bruno = agregar_miembro(casa.id, "Bruno", "BRU1", bruno_usuario.email, admin_id)
    tarea = crear_tarea(
        casa.id, "Pagar servicios", 8, actor=admin_id, responsable_id=ana.id
    )

    with pytest.raises(PermissionDeniedError):
        completar_tarea(tarea.id, bruno.id, bruno.id)

    historial = completar_tarea(tarea.id, ana.id, ana.id)
    assert historial.miembro_id == ana.id


def test_admin_puede_registrar_finalizacion_en_nombre_del_responsable(db_session):
    casa, admin_id, ana = _casa_con_admin_y_miembro(db_session)
    tarea = crear_tarea(
        casa.id, "Pagar servicios", 8, actor=admin_id, responsable_id=ana.id
    )

    historial = completar_tarea(tarea.id, ana.id, admin_id)
    assert historial.miembro_id == ana.id


def test_tarea_recurrente_completada_genera_nueva_instancia_pendiente(db_session):
    casa, admin_id, ana = _casa_con_admin_y_miembro(db_session)
    tarea = crear_tarea(
        casa.id,
        "Sacar la basura",
        3,
        actor=admin_id,
        recurrente=True,
        frecuencia="diaria",
        fecha_prevista=date.today(),
    )

    completar_tarea(tarea.id, ana.id, ana.id)
    nueva = procesar_recurrencia(tarea.id)

    assert nueva is not None
    assert nueva.id != tarea.id
    assert nueva.estado == EstadoTareaEnum.PENDIENTE
    assert nueva.recurrente is True
    assert nueva.nombre == "Sacar la basura"
    assert nueva.puntos == 3
    assert nueva.fecha_prevista == date.today() + timedelta(days=1)


def test_crear_tarea_recurrente_sin_fecha_prevista_es_rechazada(db_session):
    casa, admin_id, _ = _casa_con_admin_y_miembro(db_session)

    with pytest.raises(ValidationError):
        crear_tarea(
            casa.id, "Sacar la basura", 3, actor=admin_id, recurrente=True, frecuencia="diaria"
        )


def test_completar_tarea_recurrente_antes_de_su_fecha_prevista_es_rechazada(db_session):
    """Regresión (reportado en vivo): una tarea diaria no se puede
    completar más de una vez por día — la nueva instancia que genera
    `procesar_recurrencia` tiene `fecha_prevista` = mañana, y no debe
    poder completarse hoy."""
    casa, admin_id, ana = _casa_con_admin_y_miembro(db_session)
    tarea = crear_tarea(
        casa.id,
        "Lavar los platos",
        1,
        actor=admin_id,
        recurrente=True,
        frecuencia="diaria",
        fecha_prevista=date.today(),
    )
    completar_tarea(tarea.id, ana.id, ana.id)
    nueva = procesar_recurrencia(tarea.id)

    with pytest.raises(ConflictError):
        completar_tarea(nueva.id, ana.id, ana.id)


def test_completar_tarea_recurrente_en_su_fecha_prevista_se_permite(db_session):
    casa, admin_id, ana = _casa_con_admin_y_miembro(db_session)
    tarea = crear_tarea(
        casa.id,
        "Lavar los platos",
        1,
        actor=admin_id,
        recurrente=True,
        frecuencia="diaria",
        fecha_prevista=date.today(),
    )

    historial = completar_tarea(tarea.id, ana.id, ana.id)

    assert historial.tarea_id == tarea.id


def test_procesar_recurrencia_no_genera_instancia_si_la_tarea_no_es_recurrente(db_session):
    casa, admin_id, ana = _casa_con_admin_y_miembro(db_session)
    tarea = crear_tarea(casa.id, "Lavar los platos", 5, actor=admin_id)
    completar_tarea(tarea.id, ana.id, ana.id)

    assert procesar_recurrencia(tarea.id) is None
