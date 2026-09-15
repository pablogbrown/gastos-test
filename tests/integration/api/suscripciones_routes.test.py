"""T3 (spec `gastos-suscripcion-mensual`) — API Routes: contrato HTTP de
suscripciones.

Cubre los "Gate Criteria" de 10-verify.md: POST crea (201), GET lista,
PATCH con `activa=false` cancela y con `activa=true` responde 400.
"""
import importlib
import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.casas import casas_router
from src.api.routes.gastos import gastos_router
from src.api.routes.suscripciones import suscripciones_router
from src.db.models.usuario import Usuario
from src.services.auth_service import emitir_token


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
    migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    migration_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    migration_suscripciones = importlib.import_module("src.db.migrations.0009_suscripciones")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)
    migration_suscripciones.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.suscripcion_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(gastos_router)
    app.include_router(suscripciones_router)
    client = TestClient(app)
    client._session_factory = TestSession
    return client


def _crear_casa(client, nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    resp = client.post("/casas", json={"nombre": nombre}, headers=_bearer(usuario_id))
    assert resp.status_code == 201, resp.text
    body = resp.json()
    admin_id = body["miembros"][0]["id"] if "miembros" in body else None
    return body, usuario_id


def _crear_categoria(client, casa_id, usuario_id, nombre="Servicios"):
    resp = client.post(
        f"/casas/{casa_id}/categorias", json={"nombre": nombre}, headers=_bearer(usuario_id)
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_post_crea_suscripcion_y_genera_el_gasto_del_mes_actual(client):
    casa, usuario_id = _crear_casa(client)
    categoria_id = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/suscripciones",
        json={"descripcion": "Netflix", "importe": "5000.00", "categoria_id": categoria_id},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["descripcion"] == "Netflix"
    assert body["activa"] is True

    historial = client.get(f"/casas/{casa['id']}/gastos", headers=_bearer(usuario_id))
    assert historial.status_code == 200
    gastos = historial.json()
    assert len(gastos) == 1
    assert Decimal(gastos[0]["importe"]) == Decimal("5000.00")
    assert gastos[0]["suscripcion_id"] == body["id"]


def test_post_sin_categoria_responde_400(client):
    casa, usuario_id = _crear_casa(client)

    resp = client.post(
        f"/casas/{casa['id']}/suscripciones",
        json={"descripcion": "Netflix", "importe": "5000.00"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_get_lista_activas_e_inactivas(client):
    casa, usuario_id = _crear_casa(client)
    categoria_id = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/suscripciones",
        json={"descripcion": "Netflix", "importe": "5000.00", "categoria_id": categoria_id},
        headers=_bearer(usuario_id),
    )
    suscripcion_id = resp.json()["id"]

    listado = client.get(f"/casas/{casa['id']}/suscripciones", headers=_bearer(usuario_id))
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["id"] == suscripcion_id


def test_patch_activa_false_cancela(client):
    casa, usuario_id = _crear_casa(client)
    categoria_id = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/suscripciones",
        json={"descripcion": "Netflix", "importe": "5000.00", "categoria_id": categoria_id},
        headers=_bearer(usuario_id),
    )
    suscripcion_id = resp.json()["id"]

    cancelada = client.patch(
        f"/casas/{casa['id']}/suscripciones/{suscripcion_id}",
        json={"activa": False},
        headers=_bearer(usuario_id),
    )
    assert cancelada.status_code == 200
    assert cancelada.json()["activa"] is False


def test_patch_activa_true_responde_400(client):
    casa, usuario_id = _crear_casa(client)
    categoria_id = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/suscripciones",
        json={"descripcion": "Netflix", "importe": "5000.00", "categoria_id": categoria_id},
        headers=_bearer(usuario_id),
    )
    suscripcion_id = resp.json()["id"]

    reactivar = client.patch(
        f"/casas/{casa['id']}/suscripciones/{suscripcion_id}",
        json={"activa": True},
        headers=_bearer(usuario_id),
    )
    assert reactivar.status_code == 400


def test_crear_y_cancelar_sin_rol_admin_responde_403(client):
    casa, admin_id = _crear_casa(client)
    categoria_id = _crear_categoria(client, casa["id"], admin_id)

    email = "member@example.com"
    member_usuario = _crear_usuario_de_prueba(client._session_factory, email)
    resp_miembro = client.post(
        f"/casas/{casa['id']}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": email},
        headers=_bearer(admin_id),
    )
    assert resp_miembro.status_code == 201, resp_miembro.text

    resp = client.post(
        f"/casas/{casa['id']}/suscripciones",
        json={"descripcion": "Netflix", "importe": "5000.00", "categoria_id": categoria_id},
        headers=_bearer(member_usuario.id),
    )
    assert resp.status_code == 403

    # Admin crea una para poder intentar cancelarla como member.
    creada = client.post(
        f"/casas/{casa['id']}/suscripciones",
        json={"descripcion": "Netflix", "importe": "5000.00", "categoria_id": categoria_id},
        headers=_bearer(admin_id),
    )
    suscripcion_id = creada.json()["id"]

    cancelar = client.patch(
        f"/casas/{casa['id']}/suscripciones/{suscripcion_id}",
        json={"activa": False},
        headers=_bearer(member_usuario.id),
    )
    assert cancelar.status_code == 403
