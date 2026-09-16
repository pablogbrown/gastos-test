"""T3 (spec `gastos-estado-pago`) -- API Routes: `GastoCreate`/`GastoOut`
exponen `estado`; `PATCH /casas/{casa_id}/gastos/{gasto_id}` permite
cambiarlo, rechazando un valor invalido con 400.

Cubre TC-007.
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
from src.db.models.usuario import Usuario
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
        "0010_gasto_suscripcion_moneda",
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


def test_registrar_gasto_sin_estado_expone_pagado_por_default(client):
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
    assert resp.json()["estado"] == "pagado"


def test_registrar_gasto_con_estado_a_pagar_persiste_y_expone_estado(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Cuota futura",
            "importe": "20.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
            "estado": "a_pagar",
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["estado"] == "a_pagar"


def test_tc007_registrar_gasto_con_estado_invalido_devuelve_400(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra",
            "importe": "100.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
            "estado": "otro",
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_tc007_patch_estado_con_valor_invalido_devuelve_400(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)
    gasto = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra",
            "importe": "100.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
        },
        headers=_bearer(usuario_id),
    ).json()

    resp = client.patch(
        f"/casas/{casa['id']}/gastos/{gasto['id']}",
        json={"estado": "otro"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_patch_estado_valido_cambia_el_estado_y_lo_refleja_en_la_respuesta(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)
    gasto = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra",
            "importe": "100.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
        },
        headers=_bearer(usuario_id),
    ).json()
    assert gasto["estado"] == "pagado"

    resp = client.patch(
        f"/casas/{casa['id']}/gastos/{gasto['id']}",
        json={"estado": "a_pagar"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["estado"] == "a_pagar"

    listado = client.get(f"/casas/{casa['id']}/gastos", headers=_bearer(usuario_id))
    assert listado.json()[0]["estado"] == "a_pagar"


def test_patch_estado_de_gasto_inexistente_devuelve_404(client):
    casa, usuario_id, _admin_id = _crear_casa(client)

    resp = client.patch(
        f"/casas/{casa['id']}/gastos/{uuid.uuid4()}",
        json={"estado": "pagado"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 404
