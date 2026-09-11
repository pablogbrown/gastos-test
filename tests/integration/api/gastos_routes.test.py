"""T3 — API Routes: contrato HTTP de gastos, categorías y balance.

Cubre TC-010 (historial incluye miembros desactivados) y los contratos
del "Gate Criteria" de 10-verify.md (400 sin categoría, 403 sin rol
admin al crear categorías).
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


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.balance_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(gastos_router)
    return TestClient(app)


def _crear_casa(client, nombre="Casa Brown"):
    admin_id = str(uuid.uuid4())
    resp = client.post("/casas", json={"nombre": nombre}, headers={"X-Usuario-Id": admin_id})
    assert resp.status_code == 201, resp.text
    return resp.json(), admin_id


def _crear_categoria(client, casa_id, admin_id, nombre="Supermercado"):
    resp = client.post(
        f"/casas/{casa_id}/categorias",
        json={"nombre": nombre},
        headers={"X-Usuario-Id": admin_id},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_registrar_gasto_sin_categoria_devuelve_400(client):
    casa, admin_id = _crear_casa(client)
    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={"descripcion": "Compra", "importe": "100.00", "fecha": "2026-01-01"},
        headers={"X-Usuario-Id": admin_id},
    )
    assert resp.status_code == 400


def test_registrar_gasto_con_categoria_inexistente_devuelve_400(client):
    casa, admin_id = _crear_casa(client)
    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra",
            "importe": "100.00",
            "fecha": "2026-01-01",
            "categoria_id": str(uuid.uuid4()),
        },
        headers={"X-Usuario-Id": admin_id},
    )
    assert resp.status_code == 400


def test_miembro_sin_permisos_recibe_403_al_crear_categoria(client):
    casa, admin_id = _crear_casa(client)
    ana = client.post(
        f"/casas/{casa['id']}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1"},
        headers={"X-Usuario-Id": admin_id},
    ).json()

    resp = client.post(
        f"/casas/{casa['id']}/categorias",
        json={"nombre": "Ocio"},
        headers={"X-Usuario-Id": ana["id"]},
    )
    assert resp.status_code == 403


def test_registrar_gasto_y_consultar_balance_end_to_end(client):
    casa, admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], admin_id)

    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra semanal",
            "importe": "100.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
        },
        headers={"X-Usuario-Id": admin_id},
    )
    assert resp.status_code == 201, resp.text
    gasto = resp.json()
    assert gasto["pagado_por"] == admin_id
    assert len(gasto["participantes"]) == 1

    balance_resp = client.get(f"/casas/{casa['id']}/balance", headers={"X-Usuario-Id": admin_id})
    assert balance_resp.status_code == 200
    balance = balance_resp.json()
    assert balance["balances"][0]["miembro_id"] == admin_id


def test_historial_incluye_gastos_de_miembros_desactivados(client):
    casa, admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], admin_id)
    ana = client.post(
        f"/casas/{casa['id']}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1"},
        headers={"X-Usuario-Id": admin_id},
    ).json()

    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Gasto de Ana",
            "importe": "50.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
            "pagado_por": ana["id"],
        },
        headers={"X-Usuario-Id": admin_id},
    )
    assert resp.status_code == 201, resp.text

    client.patch(
        f"/casas/{casa['id']}/miembros/{ana['id']}",
        json={"activo": False},
        headers={"X-Usuario-Id": admin_id},
    )

    historial = client.get(f"/casas/{casa['id']}/gastos", headers={"X-Usuario-Id": admin_id})
    assert historial.status_code == 200
    descripciones = [g["descripcion"] for g in historial.json()]
    assert "Gasto de Ana" in descripciones


def test_historial_ordenado_por_fecha_descendente(client):
    casa, admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], admin_id)

    for descripcion, fecha in [("Primero", "2026-01-01"), ("Segundo", "2026-01-05")]:
        client.post(
            f"/casas/{casa['id']}/gastos",
            json={
                "descripcion": descripcion,
                "importe": "10.00",
                "fecha": fecha,
                "categoria_id": categoria["id"],
            },
            headers={"X-Usuario-Id": admin_id},
        )

    historial = client.get(f"/casas/{casa['id']}/gastos", headers={"X-Usuario-Id": admin_id})
    descripciones = [g["descripcion"] for g in historial.json()]
    assert descripciones == ["Segundo", "Primero"]
