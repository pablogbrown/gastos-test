"""Fix `fix-membresia-duplicada-actor`: `agregar_miembro` rechaza una
segunda fila `Miembro` activa para el mismo `(casa_id, usuario_id)`
(REQ-001, T1), y `resolver_actor_en_casa` nunca crashea con 500 cuando ya
existen duplicados preexistentes en la base (REQ-002, T2).

Mismo patrón de fixtures que `casas_routes.test.py` (cliente FastAPI +
SQLite en memoria + JWT real vía `emitir_token`).
"""
import importlib
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.casas import casas_router
from src.db.models.miembro import Miembro, RolEnum
from src.db.models.usuario import Usuario
from src.services.auth_service import emitir_token
from src.services.miembro_service import resolver_actor_en_casa


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


def _bearer(usuario_id):
    return {"Authorization": f"Bearer {emitir_token(usuario_id)}"}


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    importlib.import_module("src.db.migrations.0001_casas_miembros").upgrade(engine)
    importlib.import_module("src.db.migrations.0004_historial_actividad").upgrade(engine)
    importlib.import_module("src.db.migrations.0005_usuarios").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    # `agregar_miembro`/`desactivar_miembro` llaman a `registrar_actividad`
    # (spec `fix-historial-desactivacion-miembro`, mergeada junto con este
    # fix) — sin este monkeypatch, ese hook usa el `get_session` real
    # (la base configurada por `DATABASE_URL`) en vez de la SQLite aislada
    # de este test, y el INSERT falla contra una casa que no existe ahí.
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    client = TestClient(app)
    client._session_factory = TestSession  # para crear Usuarios/Miembros reales desde los tests
    return client


def _crear_casa(client, nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    resp = client.post("/casas", json={"nombre": nombre}, headers=_bearer(usuario_id))
    assert resp.status_code == 201, resp.text
    body = resp.json()
    admin_id = body["miembros"][0]["id"]
    return body, usuario_id, admin_id


def _sembrar_miembro_duplicado_directo(session_factory, casa_id, usuario_id, identificacion):
    """Inserta una fila `Miembro` directo por sesión de SQLAlchemy,
    bypaseando la API (y por lo tanto la validación de T1) a propósito —
    simula un duplicado preexistente a este fix (caution de T2 en
    01-plan-02-endurecer-resolver-actor.md)."""
    session = session_factory()
    try:
        miembro = Miembro(
            id=uuid.uuid4(),
            casa_id=uuid.UUID(casa_id) if isinstance(casa_id, str) else casa_id,
            usuario_id=usuario_id,
            nombre="Duplicado",
            identificacion=identificacion,
            rol=RolEnum.MEMBER,
            activo=True,
        )
        session.add(miembro)
        session.commit()
        session.refresh(miembro)
        return miembro
    finally:
        session.close()


# ---------------------------------------------------------------------------
# TC-001 (REQ-001): agregar dos veces el mismo Usuario a la misma casa
# ---------------------------------------------------------------------------
def test_agregar_usuario_ya_activo_en_la_misma_casa_devuelve_400(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    casa_id = casa["id"]
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")

    primero = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    )
    assert primero.status_code == 201, primero.text

    segundo = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana Otra Vez", "identificacion": "ANA2", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    )
    assert segundo.status_code == 400, segundo.text
    assert "ya es miembro activo" in segundo.json()["detail"].lower()


# ---------------------------------------------------------------------------
# TC-002 (REQ-001, control): mismo Usuario, casas distintas → ambas exitosas
# ---------------------------------------------------------------------------
def test_agregar_el_mismo_usuario_a_casas_distintas_sigue_funcionando(client):
    casa_x, usuario_x, _admin_x = _crear_casa(client, nombre="Casa X")
    casa_y, usuario_y, _admin_y = _crear_casa(client, nombre="Casa Y")
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")

    resp_x = client.post(
        f"/casas/{casa_x['id']}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_x),
    )
    assert resp_x.status_code == 201, resp_x.text

    resp_y = client.post(
        f"/casas/{casa_y['id']}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_y),
    )
    assert resp_y.status_code == 201, resp_y.text
    assert resp_x.json()["id"] != resp_y.json()["id"]


# ---------------------------------------------------------------------------
# TC-003 (REQ-002): duplicado preexistente en la base no crashea el request
# ---------------------------------------------------------------------------
def test_duplicado_preexistente_no_crashea_con_500(client):
    casa, usuario_id, admin_id = _crear_casa(client)
    casa_id = casa["id"]
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")

    # Primera fila Miembro para Ana, vía API (respeta T1).
    primero = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    )
    assert primero.status_code == 201, primero.text

    # Segunda fila Miembro activa para el mismo (casa_id, usuario_id),
    # sembrada directo en la base — bypasea T1 a propósito, simulando un
    # dato preexistente a este fix.
    _sembrar_miembro_duplicado_directo(
        client._session_factory, casa_id, ana_usuario.id, "ANA-DUP"
    )

    resp = client.get(f"/casas/{casa_id}/miembros", headers=_bearer(ana_usuario.id))
    assert resp.status_code == 200, resp.text


# ---------------------------------------------------------------------------
# TC-004 (REQ-002): resolución de actor con duplicados es repetible
# ---------------------------------------------------------------------------
def test_resolucion_de_actor_con_duplicados_es_deterministica(client):
    casa, usuario_id, admin_id = _crear_casa(client)
    casa_id = uuid.UUID(casa["id"])
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")

    primero = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    )
    assert primero.status_code == 201, primero.text

    _sembrar_miembro_duplicado_directo(
        client._session_factory, casa_id, ana_usuario.id, "ANA-DUP"
    )

    # Llama al servicio directo (misma sesión que usa la app vía
    # monkeypatch del fixture `client`) 5 veces seguidas y compara el
    # `Miembro.id` resuelto en cada llamada — TC-004 exige exactamente
    # esta comparación, no solo "ninguna devolvió 500".
    resueltos = [resolver_actor_en_casa(casa_id, ana_usuario.id) for _ in range(5)]
    assert len(set(resueltos)) == 1, f"resoluciones no deterministas: {resueltos}"
