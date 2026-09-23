"""T2 — Service Layer (unit slice): ranking_service.

Cubre TC-007 y TC-008.
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.usuario import Usuario
from src.services.casa_service import crear_casa
from src.services.exceptions import NotFoundError
from src.services.miembro_service import agregar_miembro, desactivar_miembro
from src.services.ranking_service import calcular_ranking
from src.services.tarea_service import completar_tarea, crear_tarea


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
    # 0021 (spec `avatares-economia`): `completar_tarea` ahora también
    # otorga créditos (`avatar_service.otorgar_creditos`), que requiere la
    # tabla `credito_transacciones`.
    migracion_creditos = importlib.import_module("src.db.migrations.0021_creditos")
    migracion_casas.upgrade(engine)
    migracion_tareas.upgrade(engine)
    migracion_actividad.upgrade(engine)
    migracion_usuarios.upgrade(engine)
    migracion_creditos.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.ranking_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.avatar_service.get_session", lambda: TestSession())
    yield TestSession


def test_puntos_acumulados_de_un_miembro_se_calculan_correctamente(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    for puntos in (5, 3, 10):
        tarea = crear_tarea(casa.id, f"Tarea de {puntos} puntos", puntos, actor=admin_id)
        completar_tarea(tarea.id, ana.id, ana.id)

    ranking = calcular_ranking(casa.id)

    entrada_ana = next(fila for fila in ranking if fila["miembroId"] == ana.id)
    assert entrada_ana["puntos"] == 18


def test_ranking_ordenado_de_mayor_a_menor_puntaje(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    miembros = [
        agregar_miembro(
            casa.id,
            f"M{i}",
            f"ID{i}",
            _crear_usuario_de_prueba(db_session, f"m{i}@example.com").email,
            admin_id,
        )
        for i in range(4)
    ]
    puntos_por_miembro = [5, 20, 1, 10]

    for miembro, puntos in zip(miembros, puntos_por_miembro):
        tarea = crear_tarea(casa.id, "Tarea", puntos, actor=admin_id)
        completar_tarea(tarea.id, miembro.id, miembro.id)

    ranking = calcular_ranking(casa.id)
    puntos_ordenados = [fila["puntos"] for fila in ranking]

    assert puntos_ordenados == sorted(puntos_ordenados, reverse=True)
    assert puntos_ordenados[0] == 20


def test_ranking_incluye_miembros_desactivados_con_puntos_historicos(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
    tarea = crear_tarea(casa.id, "Sacar la basura", 7, actor=admin_id)
    completar_tarea(tarea.id, ana.id, ana.id)

    desactivar_miembro(casa.id, ana.id, admin_id)

    ranking = calcular_ranking(casa.id)
    entrada_ana = next(fila for fila in ranking if fila["miembroId"] == ana.id)
    assert entrada_ana["puntos"] == 7


def test_calcular_ranking_de_casa_inexistente_lanza_not_found(db_session):
    with pytest.raises(NotFoundError):
        calcular_ranking(uuid.uuid4())
