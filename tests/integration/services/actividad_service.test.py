"""T2 — Service Layer (integration slice): hooks de actividad disparados
desde `gasto_service` y `tarea_service`.

Cubre TC-003 (registrar un gasto agrega una entrada de actividad) y
TC-004 (completar una tarea agrega entradas de actividad y de puntos).
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.historial_actividad import TipoActividadEnum
from src.db.models.usuario import Usuario
from src.services.actividad_service import obtener_actividad
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.gasto_service import registrar_gasto
from src.services.miembro_service import agregar_miembro
from src.services.tarea_service import completar_tarea, crear_tarea

_MIGRACIONES = (
    "0001_casas_miembros",
    "0002_gastos",
    "0003_tareas",
    "0004_historial_actividad",
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email) para vincular al nuevo Miembro.
    "0005_usuarios",
)
_SERVICIOS_CON_SESSION = (
    "casa_service",
    "miembro_service",
    "categoria_service",
    "gasto_service",
    "tarea_service",
    "actividad_service",
)


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
    for nombre in _MIGRACIONES:
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for servicio in _SERVICIOS_CON_SESSION:
        monkeypatch.setattr(f"src.services.{servicio}.get_session", lambda: TestSession())
    yield TestSession


def test_registrar_gasto_agrega_entrada_de_actividad(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    categoria = crear_categoria(casa.id, "Supermercado", admin_id)

    registrar_gasto(
        casa.id,
        "Compra semanal",
        Decimal("20000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )

    actividad = obtener_actividad(casa.id)
    assert len(actividad) == 1
    assert actividad[0].tipo == TipoActividadEnum.GASTO_REGISTRADO
    assert actividad[0].miembro_id == admin_id
    assert "Compra semanal" in actividad[0].descripcion


def test_crear_tarea_agrega_entrada_de_actividad(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id

    crear_tarea(casa.id, "Sacar la basura", 5, actor=admin_id)

    actividad = obtener_actividad(casa.id)
    assert len(actividad) == 1
    assert actividad[0].tipo == TipoActividadEnum.TAREA_CREADA
    assert actividad[0].miembro_id == admin_id


def test_completar_tarea_agrega_entradas_de_tarea_completada_y_puntos(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
    tarea = crear_tarea(casa.id, "Lavar los platos", 8, actor=admin_id)

    completar_tarea(tarea.id, ana.id, ana.id)

    actividad = obtener_actividad(casa.id)
    tipos = [entrada.tipo for entrada in actividad]
    assert TipoActividadEnum.TAREA_COMPLETADA in tipos
    assert TipoActividadEnum.PUNTOS_OBTENIDOS in tipos
    entradas_de_ana = [
        entrada
        for entrada in actividad
        if entrada.tipo in (TipoActividadEnum.TAREA_COMPLETADA, TipoActividadEnum.PUNTOS_OBTENIDOS)
    ]
    assert all(entrada.miembro_id == ana.id for entrada in entradas_de_ana)


def test_actividad_ordenada_de_mas_reciente_a_mas_antigua(db_session):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    crear_tarea(casa.id, "Tarea 1", 1, actor=admin_id)
    crear_tarea(casa.id, "Tarea 2", 2, actor=admin_id)

    actividad = obtener_actividad(casa.id)

    fechas = [entrada.fecha for entrada in actividad]
    assert fechas == sorted(fechas, reverse=True)
