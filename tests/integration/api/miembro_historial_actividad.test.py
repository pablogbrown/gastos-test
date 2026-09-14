"""T1 — Alta y baja de miembro registran actividad (REQ-001, REQ-002).

Cubre TC-001 (agregar miembro registra `miembro_agregado`), TC-002
(desactivar miembro registra `miembro_desactivado`) y TC-003 (una
operación rechazada no agrega ninguna entrada nueva).

`MIEMBRO_AGREGADO` ya existía en `TipoActividadEnum` pero nunca se
invocaba desde `agregar_miembro` — este archivo prueba que ahora sí se
invoca, además del nuevo `MIEMBRO_DESACTIVADO` para `desactivar_miembro`.
"""
import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.historial_actividad import TipoActividadEnum
from src.db.models.usuario import Usuario
from src.services.actividad_service import obtener_actividad
from src.services.casa_service import crear_casa
from src.services.exceptions import NotFoundError, PermissionDeniedError
from src.services.miembro_service import agregar_miembro, desactivar_miembro

_MIGRACIONES = (
    "0001_casas_miembros",
    "0004_historial_actividad",
    "0005_usuarios",
)
_SERVICIOS_CON_SESSION = (
    "casa_service",
    "miembro_service",
    "actividad_service",
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
    for nombre in _MIGRACIONES:
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for servicio in _SERVICIOS_CON_SESSION:
        monkeypatch.setattr(f"src.services.{servicio}.get_session", lambda: TestSession())
    yield TestSession


def test_agregar_miembro_exitoso_registra_actividad_miembro_agregado(db_session):
    """TC-001: alta exitosa agrega una entrada `miembro_agregado`."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")

    miembro = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    actividad = obtener_actividad(casa.id)
    assert len(actividad) == 1
    assert actividad[0].tipo == TipoActividadEnum.MIEMBRO_AGREGADO
    assert actividad[0].miembro_id == miembro.id


def test_desactivar_miembro_exitoso_registra_actividad_miembro_desactivado(db_session):
    """TC-002: baja exitosa agrega una entrada `miembro_desactivado`."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)

    desactivar_miembro(casa.id, ana.id, admin_id)

    actividad = obtener_actividad(casa.id)
    tipos = [entrada.tipo for entrada in actividad]
    assert TipoActividadEnum.MIEMBRO_DESACTIVADO in tipos
    entrada_baja = next(
        e for e in actividad if e.tipo == TipoActividadEnum.MIEMBRO_DESACTIVADO
    )
    assert entrada_baja.miembro_id == ana.id


def test_agregar_miembro_rechazado_no_agrega_actividad(db_session):
    """TC-003 (alta): email no registrado no debe dejar rastro en el
    historial, ya que la operación de negocio nunca llegó a confirmarse."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id

    with pytest.raises(NotFoundError):
        agregar_miembro(casa.id, "Ana", "ANA1", "no-registrado@example.com", admin_id)

    assert obtener_actividad(casa.id) == []


def test_desactivar_miembro_rechazado_no_agrega_actividad(db_session):
    """TC-003 (baja): un actor sin rol Administrador no debe poder
    desactivar a nadie, y el intento rechazado no agrega actividad."""
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(db_session, "ana@example.com")
    bruno_usuario = _crear_usuario_de_prueba(db_session, "bruno@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
    bruno = agregar_miembro(casa.id, "Bruno", "BRU1", bruno_usuario.email, admin_id)

    with pytest.raises(PermissionDeniedError):
        desactivar_miembro(casa.id, bruno.id, ana.id)

    actividad = obtener_actividad(casa.id)
    tipos = [entrada.tipo for entrada in actividad]
    assert TipoActividadEnum.MIEMBRO_DESACTIVADO not in tipos
