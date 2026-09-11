"""T3 — API Routes: contrato HTTP de casas/miembros.

Cubre TC-006 (403 sin permisos), TC-007 (200 admin sin restricción) y
TC-008 (comportamiento del guard de membresía usado por otras specs),
además de validar 201/400 en el flujo feliz y de error.
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


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migration = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    return TestClient(app)


def _crear_casa(client, nombre="Casa Brown"):
    admin_id = str(uuid.uuid4())
    resp = client.post("/casas", json={"nombre": nombre}, headers={"X-Usuario-Id": admin_id})
    assert resp.status_code == 201, resp.text
    return resp.json(), admin_id


def test_crear_casa_devuelve_201_con_admin_incluido(client):
    body, admin_id = _crear_casa(client)
    assert body["nombre"] == "Casa Brown"
    assert len(body["miembros"]) == 1
    assert body["miembros"][0]["id"] == admin_id
    assert body["miembros"][0]["rol"] == "admin"


def test_crear_casa_sin_nombre_devuelve_400(client):
    resp = client.post(
        "/casas", json={"nombre": ""}, headers={"X-Usuario-Id": str(uuid.uuid4())}
    )
    assert resp.status_code == 400


def test_miembro_sin_permisos_recibe_403_al_agregar_miembro(client):
    casa, admin_id = _crear_casa(client)
    casa_id = casa["id"]

    ana = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1"},
        headers={"X-Usuario-Id": admin_id},
    ).json()

    resp = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Bruno", "identificacion": "BRU1"},
        headers={"X-Usuario-Id": ana["id"]},
    )
    assert resp.status_code == 403


def test_admin_consulta_listado_completo_de_miembros_sin_restriccion(client):
    casa, admin_id = _crear_casa(client)
    casa_id = casa["id"]
    client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1"},
        headers={"X-Usuario-Id": admin_id},
    )

    resp = client.get(f"/casas/{casa_id}/miembros", headers={"X-Usuario-Id": admin_id})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_desactivar_miembro_devuelve_200_y_activo_false(client):
    casa, admin_id = _crear_casa(client)
    casa_id = casa["id"]
    ana = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1"},
        headers={"X-Usuario-Id": admin_id},
    ).json()

    resp = client.patch(
        f"/casas/{casa_id}/miembros/{ana['id']}",
        json={"activo": False},
        headers={"X-Usuario-Id": admin_id},
    )
    assert resp.status_code == 200
    assert resp.json()["activo"] is False
