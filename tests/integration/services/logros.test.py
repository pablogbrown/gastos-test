"""T2 (spec `gamificacion-puntos`) — logros.

Cubre TC-005: completar la primera tarea desbloquea el logro
correspondiente; cruzar un umbral de puntos o de racha desbloquea el
logro asociado exactamente una vez, nunca duplicado.
"""
import importlib
import uuid
from datetime import date, datetime, time, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.historial_tarea import HistorialTarea
from src.db.models.usuario import Usuario
from src.services.casa_service import crear_casa
from src.services.logro_service import evaluar_logros, listar_logros_obtenidos
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
    migracion_gamificacion = importlib.import_module("src.db.migrations.0020_gamificacion")
    # 0021 (spec `avatares-economia`): `completar_tarea` ahora también
    # otorga créditos (`avatar_service.otorgar_creditos`), que requiere la
    # tabla `credito_transacciones`.
    migracion_creditos = importlib.import_module("src.db.migrations.0021_creditos")
    migracion_casas.upgrade(engine)
    migracion_tareas.upgrade(engine)
    migracion_actividad.upgrade(engine)
    migracion_usuarios.upgrade(engine)
    migracion_gamificacion.upgrade(engine)
    migracion_creditos.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.ranking_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.logro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.avatar_service.get_session", lambda: TestSession())
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


def test_completar_la_primera_tarea_desbloquea_el_logro_correspondiente(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    tarea = crear_tarea(casa.id, "Sacar la basura", 5, actor=admin_id)
    completar_tarea(tarea.id, ana.id, ana.id)

    # `completar_tarea` ya dispara `evaluar_logros` internamente
    # (`tarea_service.completar_tarea`, después del commit).
    logros = listar_logros_obtenidos(casa.id)
    ids_logro = {logro.logro_id for logro in logros if logro.miembro_id == ana.id}
    assert "primera_tarea" in ids_logro


def test_cruzar_un_umbral_de_puntos_desbloquea_el_logro_asociado(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    tarea = crear_tarea(casa.id, "Tarea de 100 puntos", 100, actor=admin_id)
    completar_tarea(tarea.id, ana.id, ana.id)

    logros = listar_logros_obtenidos(casa.id)
    ids_logro = {logro.logro_id for logro in logros if logro.miembro_id == ana.id}
    assert "cien_puntos" in ids_logro


def test_logro_nunca_se_duplica_al_completar_mas_tareas(db_session):
    """Completar una segunda tarea que ya cruzó el umbral de nuevo no debe
    insertar una segunda fila del mismo logro para el mismo miembro."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    tarea_uno = crear_tarea(casa.id, "Tarea 1", 5, actor=admin_id)
    completar_tarea(tarea_uno.id, ana.id, ana.id)
    tarea_dos = crear_tarea(casa.id, "Tarea 2", 5, actor=admin_id)
    completar_tarea(tarea_dos.id, ana.id, ana.id)

    logros = listar_logros_obtenidos(casa.id)
    entradas_primera_tarea = [
        logro for logro in logros if logro.miembro_id == ana.id and logro.logro_id == "primera_tarea"
    ]
    assert len(entradas_primera_tarea) == 1


def test_evaluar_logros_llamado_dos_veces_no_duplica(db_session):
    """Llamar `evaluar_logros` explícitamente más de una vez para el mismo
    estado no crea filas duplicadas (chequeo en el service layer antes del
    insert — [SERV-01], nunca un constraint de DB)."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    tarea = crear_tarea(casa.id, "Tarea", 5, actor=admin_id)
    completar_tarea(tarea.id, ana.id, ana.id)

    evaluar_logros(casa.id, ana.id)
    evaluar_logros(casa.id, ana.id)

    logros = listar_logros_obtenidos(casa.id)
    entradas = [logro for logro in logros if logro.miembro_id == ana.id and logro.logro_id == "primera_tarea"]
    assert len(entradas) == 1


def test_racha_de_siete_dias_desbloquea_el_logro_de_racha(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    hoy = date.today()
    for offset in range(6, -1, -1):
        tarea = crear_tarea(casa.id, "Tarea", 1, actor=admin_id)
        _completar_en_fecha(db_session, tarea.id, ana.id, ana.id, hoy - timedelta(days=offset))

    # `_completar_en_fecha` ya llamó `evaluar_logros` (vía `completar_tarea`)
    # con `completada_en` todavía en el valor por defecto (hoy) al momento
    # del hook — reevaluar explícitamente una vez reescritas las fechas.
    evaluar_logros(casa.id, ana.id)

    logros = listar_logros_obtenidos(casa.id)
    ids_logro = {logro.logro_id for logro in logros if logro.miembro_id == ana.id}
    assert "racha_siete" in ids_logro


def test_completar_tarea_sin_cruzar_ningun_umbral_no_crea_logros(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    # La PRIMERA tarea siempre desbloquea "primera_tarea" — para probar el
    # caso "sin ningún logro nuevo" hay que completar una SEGUNDA tarea que
    # no cruce ningún otro umbral (puntos/racha/cantidad).
    tarea_uno = crear_tarea(casa.id, "Tarea 1", 1, actor=admin_id)
    completar_tarea(tarea_uno.id, ana.id, ana.id)
    logros_tras_primera = {l.logro_id for l in listar_logros_obtenidos(casa.id) if l.miembro_id == ana.id}
    assert logros_tras_primera == {"primera_tarea"}

    tarea_dos = crear_tarea(casa.id, "Tarea 2", 1, actor=admin_id)
    completar_tarea(tarea_dos.id, ana.id, ana.id)
    logros_tras_segunda = {l.logro_id for l in listar_logros_obtenidos(casa.id) if l.miembro_id == ana.id}
    assert logros_tras_segunda == {"primera_tarea"}
