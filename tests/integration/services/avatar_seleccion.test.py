"""T3 (spec `avatares-economia`) — desbloqueo por nivel + selección de
avatar.

Cubre TC-004 (segunda mitad: una raza ya seleccionada se conserva aunque
salga de ventana — la primera mitad vive en `avatar_catalogo.test.py`,
T2), TC-005 (nivel insuficiente rechazado), TC-006 (selección permitida
dentro del nivel), TC-007 (sin selección, `None`) y TC-008 (cambiar de
raza reemplaza la anterior).
"""
import importlib
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.avatar_personaje import AvatarPersonaje
from src.db.models.usuario import Usuario
from src.services.avatar_service import (
    listar_avatares_disponibles,
    listar_catalogo,
    obtener_avatar_seleccionado,
    seleccionar_avatar,
)
from src.services.casa_service import crear_casa
from src.services.exceptions import PermissionDeniedError
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
    migracion_catalogo = importlib.import_module("src.db.migrations.0022_avatar_catalogo")
    migracion_seleccion = importlib.import_module("src.db.migrations.0023_avatar_seleccionado")
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
    migracion_catalogo.upgrade(engine)
    migracion_seleccion.upgrade(engine)
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


def _subir_a_activo(casa_id, admin_id, beneficiario_id):
    """Completa una tarea de 50 puntos — umbral exacto de "Activo" en
    `ranking_service.NIVELES`."""
    tarea = crear_tarea(casa_id, "Tarea de nivel", 50, actor=admin_id)
    completar_tarea(tarea.id, beneficiario_id, beneficiario_id)


def test_avatar_sin_seleccion_previa_es_null(db_session):
    """TC-007: sin selección previa, el avatar es `None`."""
    _, _, ana = _casa_con_beneficiario(db_session)
    assert obtener_avatar_seleccionado(ana.id) is None


def test_miembro_novato_no_puede_seleccionar_raza_de_nivel_activo(db_session):
    """TC-005: un miembro en nivel Novato no puede seleccionar una raza
    que requiere nivel Activo."""
    _, _, ana = _casa_con_beneficiario(db_session)
    disponibles = listar_avatares_disponibles(ana.id)
    assert all(avatar.nivel_requerido == "Novato" for avatar in disponibles)

    # Ninguna raza de nivel superior aparece en `disponibles` — se busca
    # directo en el catálogo completo (T2) para intentar seleccionarla
    # igual y confirmar el rechazo.
    raza_activo = next(
        avatar for avatar in listar_catalogo(ana.id) if avatar.nivel_requerido == "Activo"
    )
    with pytest.raises(PermissionDeniedError):
        seleccionar_avatar(ana.id, raza_activo.id)


def test_miembro_activo_puede_seleccionar_raza_de_novato_o_activo(db_session):
    """TC-006: un miembro en nivel Activo puede seleccionar una raza de
    nivel Novato o Activo."""
    casa, admin_id, ana = _casa_con_beneficiario(db_session)
    _subir_a_activo(casa.id, admin_id, ana.id)

    disponibles = listar_avatares_disponibles(ana.id)
    niveles_disponibles = {avatar.nivel_requerido for avatar in disponibles}
    assert niveles_disponibles == {"Novato", "Activo"}

    raza_activo = next(avatar for avatar in disponibles if avatar.nivel_requerido == "Activo")
    seleccion = seleccionar_avatar(ana.id, raza_activo.id)
    assert seleccion.avatar_personaje_id == raza_activo.id
    assert obtener_avatar_seleccionado(ana.id).id == raza_activo.id


def test_cambiar_de_raza_reemplaza_la_seleccion_anterior(db_session):
    """TC-008: cambiar de raza ya desbloqueada reemplaza la selección
    anterior, sin acumular filas."""
    _, _, ana = _casa_con_beneficiario(db_session)
    disponibles = listar_avatares_disponibles(ana.id)
    assert len(disponibles) >= 2, "el seed necesita al menos 2 razas Novato para este test"

    primera, segunda = disponibles[0], disponibles[1]
    seleccionar_avatar(ana.id, primera.id)
    assert obtener_avatar_seleccionado(ana.id).id == primera.id

    seleccionar_avatar(ana.id, segunda.id)
    assert obtener_avatar_seleccionado(ana.id).id == segunda.id


def test_seleccionar_una_raza_inexistente_es_rechazada(db_session):
    """`seleccionar_avatar` rechaza una raza inexistente exactamente igual
    que una de nivel superior (ambas ausentes de
    `listar_avatares_disponibles`)."""
    _, _, ana = _casa_con_beneficiario(db_session)
    with pytest.raises(PermissionDeniedError):
        seleccionar_avatar(ana.id, uuid.uuid4())


def test_raza_ya_seleccionada_se_conserva_aunque_salga_de_ventana(db_session):
    """TC-004 (segunda mitad): un miembro que ya eligió una raza la
    conserva en su catálogo/disponibles aunque esa raza salga de ventana
    después — solo se oculta para quien todavía NO la había elegido."""
    _, _, ana = _casa_con_beneficiario(db_session)
    disponibles = listar_avatares_disponibles(ana.id)
    raza = disponibles[0]
    seleccionar_avatar(ana.id, raza.id)

    # La raza sale de ventana DESPUÉS de haber sido elegida.
    session = db_session()
    try:
        session.execute(
            update(AvatarPersonaje.__table__)
            .where(AvatarPersonaje.id == raza.id)
            .values(
                disponible_desde=date.today() - timedelta(days=30),
                disponible_hasta=date.today() - timedelta(days=1),
            )
        )
        session.commit()
    finally:
        session.close()

    razas_en_catalogo = {avatar.id for avatar in listar_catalogo(ana.id)}
    assert raza.id in razas_en_catalogo
    assert obtener_avatar_seleccionado(ana.id).id == raza.id

    # Otro miembro que NUNCA la eligió no la ve — solo se conserva para
    # quien ya la tenía.
    otra_casa_usuario_id = uuid.uuid4()
    otra_casa = crear_casa("Casa Gómez", otra_casa_usuario_id)
    otro_admin_id = otra_casa.miembros[0].id
    beto_usuario = _crear_usuario_de_prueba(db_session, "beto@example.com")
    beto = agregar_miembro(otra_casa.id, "Beto", "BETO1", beto_usuario.email, otro_admin_id)
    razas_para_beto = {avatar.id for avatar in listar_catalogo(beto.id)}
    assert raza.id not in razas_para_beto
