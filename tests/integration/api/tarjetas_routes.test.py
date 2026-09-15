"""T3 (spec `tarjetas-credito`) — API Routes: contrato HTTP de tarjetas.

Cubre los "Gate Criteria" de 10-verify.md: TC-001 a TC-004 a nivel HTTP.
"""
import importlib
import uuid
from datetime import date, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.casas import casas_router
from src.api.routes.tarjetas import tarjetas_router
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
    migration_tarjetas = importlib.import_module("src.db.migrations.0011_tarjetas_credito")
    migration_casas.upgrade(engine)
    migration_tarjetas.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarjeta_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(tarjetas_router)
    client = TestClient(app)
    client._session_factory = TestSession
    return client


def _crear_casa_directo(nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    casa = crear_casa(nombre, usuario_id)
    admin_id = casa.miembros[0].id
    return casa, usuario_id, admin_id


def _payload_valido():
    hoy = date.today()
    return {
        "banco": "BBVA",
        "nombre": "Visa Platinum",
        "ultimos_digitos": "1234",
        "fecha_cierre_actual": (hoy - timedelta(days=10)).isoformat(),
        "fecha_vencimiento_actual": (hoy + timedelta(days=30)).isoformat(),
    }


def test_tc001_post_crea_tarjeta_y_aparece_en_el_listado(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.post(
        f"/casas/{casa.id}/tarjetas", json=_payload_valido(), headers=_bearer(usuario_id)
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nombre"] == "Visa Platinum"
    assert body["activa"] is True
    assert body["saldo_actual_ars"] is None

    listado = client.get(f"/casas/{casa.id}/tarjetas", headers=_bearer(usuario_id))
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["id"] == body["id"]


def test_tc002_post_sin_banco_responde_400(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    payload = _payload_valido()
    payload["banco"] = ""

    resp = client.post(f"/casas/{casa.id}/tarjetas", json=payload, headers=_bearer(usuario_id))
    assert resp.status_code == 400


def test_tc003_patch_edita_vencimiento_y_persiste(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    creada = client.post(
        f"/casas/{casa.id}/tarjetas", json=_payload_valido(), headers=_bearer(usuario_id)
    )
    tarjeta_id = creada.json()["id"]
    nuevo_vencimiento = (date.today() + timedelta(days=60)).isoformat()

    resp = client.patch(
        f"/casas/{casa.id}/tarjetas/{tarjeta_id}",
        json={"fecha_vencimiento_actual": nuevo_vencimiento},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["fecha_vencimiento_actual"] == nuevo_vencimiento

    listado = client.get(f"/casas/{casa.id}/tarjetas", headers=_bearer(usuario_id))
    assert listado.json()[0]["fecha_vencimiento_actual"] == nuevo_vencimiento


def test_tc004_delete_saca_la_tarjeta_del_listado_activo(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    creada = client.post(
        f"/casas/{casa.id}/tarjetas", json=_payload_valido(), headers=_bearer(usuario_id)
    )
    tarjeta_id = creada.json()["id"]

    resp = client.delete(f"/casas/{casa.id}/tarjetas/{tarjeta_id}", headers=_bearer(usuario_id))
    assert resp.status_code == 204

    listado = client.get(f"/casas/{casa.id}/tarjetas", headers=_bearer(usuario_id))
    assert listado.json() == []


def test_patch_tarjeta_inexistente_responde_404(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.patch(
        f"/casas/{casa.id}/tarjetas/{uuid.uuid4()}",
        json={"saldo_actual_ars": "1000.00"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 404


def test_delete_tarjeta_inexistente_responde_404(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.delete(f"/casas/{casa.id}/tarjetas/{uuid.uuid4()}", headers=_bearer(usuario_id))
    assert resp.status_code == 404


def test_post_sin_jwt_devuelve_401(client):
    casa, _usuario_id, _admin_id = _crear_casa_directo()
    resp = client.post(f"/casas/{casa.id}/tarjetas", json=_payload_valido())
    assert resp.status_code == 401


def test_usuario_no_miembro_de_la_casa_recibe_403(client):
    casa, _usuario_id, _admin_id = _crear_casa_directo()
    usuario_ajeno = uuid.uuid4()

    resp = client.post(
        f"/casas/{casa.id}/tarjetas", json=_payload_valido(), headers=_bearer(usuario_ajeno)
    )
    assert resp.status_code == 403
