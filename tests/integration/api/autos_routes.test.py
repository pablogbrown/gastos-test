"""T3 (spec `mantenimiento-autos`) — API Routes: contrato HTTP de autos +
`auto_id`/`autoId` en mantenimiento.

Cubre TC-001 a TC-005 a nivel HTTP.
"""
import importlib
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.autos import autos_router
from src.api.routes.casas import casas_router
from src.api.routes.mantenimiento import mantenimiento_router
from src.services.auth_service import emitir_token
from src.services.casa_service import crear_casa


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
    migration_mantenimiento = importlib.import_module("src.db.migrations.0017_mantenimiento")
    migration_autos = importlib.import_module("src.db.migrations.0018_mantenimiento_autos")
    migration_casas.upgrade(engine)
    migration_mantenimiento.upgrade(engine)
    migration_autos.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.auto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.mantenimiento_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(autos_router)
    app.include_router(mantenimiento_router)
    return TestClient(app)


def _crear_casa_directo(nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    casa = crear_casa(nombre, usuario_id)
    admin_id = casa.miembros[0].id
    return casa, usuario_id, admin_id


def test_tc001_post_crea_auto_y_aparece_en_el_listado(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.post(
        f"/casas/{casa.id}/autos",
        json={"marca": "Toyota", "modelo": "Corolla", "patente": "AB123CD", "anio": 2020},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["marca"] == "Toyota"
    assert body["modelo"] == "Corolla"
    assert body["patente"] == "AB123CD"
    assert body["anio"] == 2020

    listado = client.get(f"/casas/{casa.id}/autos", headers=_bearer(usuario_id))
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["id"] == body["id"]


def test_post_auto_sin_marca_responde_400(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.post(
        f"/casas/{casa.id}/autos",
        json={"modelo": "Corolla"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_tc002_post_item_con_auto_id_queda_asociado(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    auto = client.post(
        f"/casas/{casa.id}/autos",
        json={"marca": "Toyota", "modelo": "Corolla"},
        headers=_bearer(usuario_id),
    ).json()

    resp = client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={"nombre": "Cambio de aceite", "auto_id": auto["id"]},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["auto_id"] == auto["id"]


def test_tc003_listar_sin_autoid_devuelve_solo_los_de_la_casa(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    auto = client.post(
        f"/casas/{casa.id}/autos",
        json={"marca": "Toyota", "modelo": "Corolla"},
        headers=_bearer(usuario_id),
    ).json()
    client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={"nombre": "Pintar el living"},
        headers=_bearer(usuario_id),
    )
    client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={"nombre": "Cambio de aceite", "auto_id": auto["id"]},
        headers=_bearer(usuario_id),
    )

    resp = client.get(f"/casas/{casa.id}/mantenimiento", headers=_bearer(usuario_id))
    assert resp.status_code == 200
    nombres = {item["nombre"] for item in resp.json()}
    assert nombres == {"Pintar el living"}


def test_tc003_listar_filtrando_por_autoid_devuelve_solo_los_de_ese_auto(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    auto = client.post(
        f"/casas/{casa.id}/autos",
        json={"marca": "Toyota", "modelo": "Corolla"},
        headers=_bearer(usuario_id),
    ).json()
    client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={"nombre": "Pintar el living"},
        headers=_bearer(usuario_id),
    )
    client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={"nombre": "Cambio de aceite", "auto_id": auto["id"]},
        headers=_bearer(usuario_id),
    )

    resp = client.get(
        f"/casas/{casa.id}/mantenimiento",
        params={"autoId": auto["id"]},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 200
    nombres = {item["nombre"] for item in resp.json()}
    assert nombres == {"Cambio de aceite"}


def test_tc005_auto_de_otra_casa_responde_404(client):
    casa1, usuario1, _admin1 = _crear_casa_directo("Casa 1")
    casa2, usuario2, _admin2 = _crear_casa_directo("Casa 2")
    auto_de_casa2 = client.post(
        f"/casas/{casa2.id}/autos",
        json={"marca": "Toyota", "modelo": "Corolla"},
        headers=_bearer(usuario2),
    ).json()

    resp = client.post(
        f"/casas/{casa1.id}/mantenimiento",
        json={"nombre": "Cambio de aceite", "auto_id": auto_de_casa2["id"]},
        headers=_bearer(usuario1),
    )
    assert resp.status_code == 404
