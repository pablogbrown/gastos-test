"""Spec `invitar-miembro-pendiente`: invitar a alguien por email antes de
que tenga cuenta, y vincular la membresía automáticamente cuando se
registra.

Cubre TC-001, TC-002, TC-003, TC-004, TC-006 vía la API real (POST
`/casas/{id}/miembros` y POST `/auth/registro`, mismo cliente FastAPI +
SQLite en memoria que `miembro_membresia_unica.test.py`). TC-005 se
cubre en `tests/unit/services/auth_service.test.py` — el "control" de
registrar sin membresías pendientes ya está cubierto por el resto de esa
suite, que sigue en verde sin ningún dato pendiente sembrado.
"""
import importlib
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.auth import auth_router
from src.api.routes.casas import casas_router
from src.services.auth_service import emitir_token


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
    monkeypatch.setattr("src.services.auth_service.get_session", lambda: TestSession())
    # `agregar_miembro` llama a `registrar_actividad` — sin este
    # monkeypatch, ese hook usa el `get_session` real en vez de la SQLite
    # aislada de este test (mismo motivo que `miembro_membresia_unica.test.py`).
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(casas_router)
    client = TestClient(app)
    return client


def _crear_casa(client, nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    resp = client.post("/casas", json={"nombre": nombre}, headers=_bearer(usuario_id))
    assert resp.status_code == 201, resp.text
    return resp.json(), usuario_id


def _invitar(client, casa_id, admin_usuario_id, email, nombre="Ana", identificacion="ANA1"):
    return client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": nombre, "identificacion": identificacion, "email": email},
        headers=_bearer(admin_usuario_id),
    )


# ---------------------------------------------------------------------------
# TC-001: alta con un email sin Usuario registrado crea membresía pendiente
# ---------------------------------------------------------------------------
def test_invitar_email_sin_usuario_registrado_crea_membresia_pendiente(client):
    casa, admin_usuario_id = _crear_casa(client)

    resp = _invitar(client, casa["id"], admin_usuario_id, "no-registrado@example.com")

    assert resp.status_code == 201, resp.text
    assert resp.json()["usuario_id"] is None


# ---------------------------------------------------------------------------
# TC-002 (control): alta con un email ya registrado sigue vinculando de
# inmediato, exactamente como hoy.
# ---------------------------------------------------------------------------
def test_invitar_email_ya_registrado_vincula_de_inmediato(client):
    casa, admin_usuario_id = _crear_casa(client)
    registro = client.post(
        "/auth/registro", json={"email": "ana@example.com", "password": "hunter2"}
    )
    assert registro.status_code == 201, registro.text
    ana_id = registro.json()["id"]

    resp = _invitar(client, casa["id"], admin_usuario_id, "ana@example.com")

    assert resp.status_code == 201, resp.text
    assert resp.json()["usuario_id"] == ana_id


# ---------------------------------------------------------------------------
# TC-006: una segunda invitación pendiente al mismo email, en la misma
# casa, es rechazada mientras la primera siga sin vincularse.
# ---------------------------------------------------------------------------
def test_doble_invitacion_pendiente_al_mismo_email_es_rechazada(client):
    casa, admin_usuario_id = _crear_casa(client)
    primera = _invitar(client, casa["id"], admin_usuario_id, "pendiente@example.com")
    assert primera.status_code == 201, primera.text

    segunda = _invitar(
        client,
        casa["id"],
        admin_usuario_id,
        "pendiente@example.com",
        nombre="Otro Nombre",
        identificacion="OTRO1",
    )

    assert segunda.status_code == 400, segunda.text
    assert "ya es miembro activo" in segunda.json()["detail"].lower()


# ---------------------------------------------------------------------------
# TC-003: registrarse vincula una membresía pendiente con el mismo email.
# ---------------------------------------------------------------------------
def test_registrarse_vincula_una_membresia_pendiente(client):
    casa, admin_usuario_id = _crear_casa(client)
    invitacion = _invitar(client, casa["id"], admin_usuario_id, "x@example.com")
    assert invitacion.status_code == 201, invitacion.text
    miembro_id = invitacion.json()["id"]

    registro = client.post(
        "/auth/registro", json={"email": "x@example.com", "password": "hunter2"}
    )
    assert registro.status_code == 201, registro.text
    nuevo_usuario_id = registro.json()["id"]

    listado = client.get(
        f"/casas/{casa['id']}/miembros", headers=_bearer(uuid.UUID(nuevo_usuario_id))
    )
    assert listado.status_code == 200, listado.text
    miembro_vinculado = next(m for m in listado.json() if m["id"] == miembro_id)
    assert miembro_vinculado["usuario_id"] == nuevo_usuario_id


# ---------------------------------------------------------------------------
# TC-004: registrarse vincula TODAS las membresías pendientes con ese
# email, en varias casas a la vez.
# ---------------------------------------------------------------------------
def test_registrarse_vincula_pendientes_en_varias_casas(client):
    casa_a, admin_a = _crear_casa(client, nombre="Casa A")
    casa_b, admin_b = _crear_casa(client, nombre="Casa B")

    inv_a = _invitar(client, casa_a["id"], admin_a, "multi@example.com", identificacion="M-A")
    assert inv_a.status_code == 201, inv_a.text
    inv_b = _invitar(client, casa_b["id"], admin_b, "multi@example.com", identificacion="M-B")
    assert inv_b.status_code == 201, inv_b.text

    registro = client.post(
        "/auth/registro", json={"email": "multi@example.com", "password": "hunter2"}
    )
    assert registro.status_code == 201, registro.text
    nuevo_usuario_id = registro.json()["id"]

    listado_a = client.get(
        f"/casas/{casa_a['id']}/miembros", headers=_bearer(uuid.UUID(nuevo_usuario_id))
    )
    listado_b = client.get(
        f"/casas/{casa_b['id']}/miembros", headers=_bearer(uuid.UUID(nuevo_usuario_id))
    )
    assert listado_a.status_code == 200, listado_a.text
    assert listado_b.status_code == 200, listado_b.text

    miembro_a = next(m for m in listado_a.json() if m["identificacion"] == "M-A")
    miembro_b = next(m for m in listado_b.json() if m["identificacion"] == "M-B")
    assert miembro_a["usuario_id"] == nuevo_usuario_id
    assert miembro_b["usuario_id"] == nuevo_usuario_id
