"""T2 (spec `gastos-vista-mensual`) — API Routes: `GET
/casas/{casa_id}/gastos?mes=` filtra la respuesta HTTP.

Cubre TC-003 — mismo patrón que `GET .../balance?mes=` ya existente
(`tests/integration/api/gastos_routes.test.py`, spec `balance-mensual`).
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
    for nombre in (
        "0001_casas_miembros",
        "0002_gastos",
        "0004_historial_actividad",
        "0005_usuarios",
        "0009_suscripciones",
    ):
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for modulo in (
        "src.services.casa_service",
        "src.services.miembro_service",
        "src.services.categoria_service",
        "src.services.gasto_service",
        "src.services.balance_service",
        "src.services.actividad_service",
        "src.services.suscripcion_service",
    ):
        monkeypatch.setattr(f"{modulo}.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(gastos_router)
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


def _registrar_gasto(client, casa_id, usuario_id, categoria_id, descripcion, fecha):
    resp = client.post(
        f"/casas/{casa_id}/gastos",
        json={
            "descripcion": descripcion,
            "importe": "100.00",
            "fecha": fecha,
            "categoria_id": categoria_id,
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_tc003_gastos_con_mes_explicito_filtra_la_respuesta(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    _registrar_gasto(
        client, casa["id"], usuario_id, categoria["id"], "Gasto de agosto", "2026-08-15"
    )
    _registrar_gasto(
        client, casa["id"], usuario_id, categoria["id"], "Gasto de septiembre", "2026-09-01"
    )

    resp_septiembre = client.get(
        f"/casas/{casa['id']}/gastos?mes=2026-09", headers=_bearer(usuario_id)
    )
    assert resp_septiembre.status_code == 200
    descripciones_septiembre = {g["descripcion"] for g in resp_septiembre.json()}
    assert descripciones_septiembre == {"Gasto de septiembre"}

    resp_agosto = client.get(
        f"/casas/{casa['id']}/gastos?mes=2026-08", headers=_bearer(usuario_id)
    )
    descripciones_agosto = {g["descripcion"] for g in resp_agosto.json()}
    assert descripciones_agosto == {"Gasto de agosto"}


def test_gastos_con_mes_de_formato_invalido_devuelve_400(client):
    casa, usuario_id, _admin_id = _crear_casa(client)

    resp = client.get(
        f"/casas/{casa['id']}/gastos?mes=fecha-invalida",
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_gastos_sin_mes_sigue_devolviendo_todos_los_gastos(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    _registrar_gasto(
        client, casa["id"], usuario_id, categoria["id"], "Gasto de agosto", "2026-08-15"
    )
    _registrar_gasto(
        client, casa["id"], usuario_id, categoria["id"], "Gasto de septiembre", "2026-09-01"
    )

    resp = client.get(f"/casas/{casa['id']}/gastos", headers=_bearer(usuario_id))
    assert resp.status_code == 200
    assert len(resp.json()) == 2
