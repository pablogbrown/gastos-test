"""T3 (spec `gastos-multi-moneda`) — API Routes: los endpoints de
gastos/suscripciones/balance aceptan y exponen `moneda`.

Cubre TC-008.
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
    monkeypatch.setattr("src.services.balance_service.get_session", lambda: TestSession())
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
    admin_id = body["miembros"][0]["id"]
    return body, usuario_id, admin_id


def _crear_categoria(client, casa_id, usuario_id, nombre="Supermercado"):
    resp = client.post(
        f"/casas/{casa_id}/categorias",
        json={"nombre": nombre},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_tc008_registrar_gasto_con_moneda_invalida_devuelve_400(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra",
            "importe": "100.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
            "moneda": "EUR",
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_tc008_crear_suscripcion_con_moneda_invalida_devuelve_400(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/suscripciones",
        json={
            "descripcion": "Netflix",
            "importe": "15.00",
            "categoria_id": categoria["id"],
            "moneda": "EUR",
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_registrar_gasto_con_moneda_usd_persiste_y_expone_moneda(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra en dólares",
            "importe": "20.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
            "moneda": "USD",
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["moneda"] == "USD"


def test_registrar_gasto_sin_moneda_expone_ars_por_default(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra",
            "importe": "20.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["moneda"] == "ARS"


def test_crear_suscripcion_con_moneda_usd_persiste_y_expone_moneda(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/suscripciones",
        json={
            "descripcion": "Netflix",
            "importe": "15.00",
            "categoria_id": categoria["id"],
            "moneda": "USD",
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["moneda"] == "USD"

    listado = client.get(f"/casas/{casa['id']}/suscripciones", headers=_bearer(usuario_id))
    assert listado.status_code == 200
    assert listado.json()[0]["moneda"] == "USD"


def test_balance_expone_moneda_en_cada_fila_y_en_transferencias(client):
    casa, usuario_id, admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")
    ana = client.post(
        f"/casas/{casa['id']}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    ).json()

    client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Super en pesos",
            "importe": "40000.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
            "participantes": [admin_id, ana["id"]],
        },
        headers=_bearer(usuario_id),
    )
    client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra en dólares",
            "importe": "40.00",
            "fecha": "2026-01-02",
            "categoria_id": categoria["id"],
            "participantes": [admin_id, ana["id"]],
            "moneda": "USD",
            "pagado_por": ana["id"],
        },
        headers=_bearer(usuario_id),
    )

    resp = client.get(f"/casas/{casa['id']}/balance?mes=2026-01", headers=_bearer(usuario_id))
    assert resp.status_code == 200
    body = resp.json()

    monedas_balances = {fila["moneda"] for fila in body["balances"]}
    assert monedas_balances == {"ARS", "USD"}

    monedas_transferencias = {t["moneda"] for t in body["transferencias"]}
    assert monedas_transferencias == {"ARS", "USD"}
