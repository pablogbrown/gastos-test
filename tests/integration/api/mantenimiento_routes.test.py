"""T3 (spec `mantenimiento-casa`) — API Routes: contrato HTTP de
mantenimiento + `mantenimientoConAlerta` en el dashboard.

Cubre TC-001 a TC-004, TC-006, TC-007 a nivel HTTP, más el aditivo del
dashboard (10-verify.md).
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
from src.api.routes.dashboard import dashboard_router
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
    migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")
    migration_tareas = importlib.import_module("src.db.migrations.0003_tareas")
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    migration_suscripciones = importlib.import_module("src.db.migrations.0009_suscripciones")
    migration_tarjetas = importlib.import_module("src.db.migrations.0011_tarjetas_credito")
    migration_mantenimiento = importlib.import_module("src.db.migrations.0017_mantenimiento")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_tareas.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_suscripciones.upgrade(engine)
    migration_tarjetas.upgrade(engine)
    migration_mantenimiento.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.mantenimiento_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarjeta_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.suscripcion_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.balance_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.ranking_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(mantenimiento_router)
    app.include_router(dashboard_router)
    client = TestClient(app)
    client._session_factory = TestSession
    return client


def _crear_casa_directo(nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    casa = crear_casa(nombre, usuario_id)
    admin_id = casa.miembros[0].id
    return casa, usuario_id, admin_id


def test_tc001_post_crea_item_y_aparece_en_el_listado(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={"nombre": "Arreglar el reflector de la entrada"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nombre"] == "Arreglar el reflector de la entrada"
    assert body["estado"] == "pendiente"

    listado = client.get(f"/casas/{casa.id}/mantenimiento", headers=_bearer(usuario_id))
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["id"] == body["id"]


def test_tc002_post_recurrente_sin_periodicidad_ni_fecha_responde_400(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={"nombre": "Poner membrana al techo", "recurrente": True},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_tc003_post_con_materiales_persisten_cada_uno(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={
            "nombre": "Poner membrana al techo",
            "recurrente": True,
            "periodicidad": "anual",
            "fecha_estimada": (date.today() + timedelta(days=90)).isoformat(),
            "materiales": [
                {"nombre": "Membrana asfáltica", "cantidad": 2},
                {"nombre": "Silicona", "cantidad": 1},
            ],
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    materiales = resp.json()["materiales"]
    assert len(materiales) == 2
    assert all(m["conseguido"] is False for m in materiales)


def test_tc004_patch_material_marca_conseguido(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    creado = client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={"nombre": "Pintar el living", "materiales": [{"nombre": "Pintura", "cantidad": 3}]},
        headers=_bearer(usuario_id),
    )
    item_id = creado.json()["id"]
    material_id = creado.json()["materiales"][0]["id"]

    resp = client.patch(
        f"/casas/{casa.id}/mantenimiento/{item_id}/materiales/{material_id}",
        json={"conseguido": True},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["conseguido"] is True


def test_tc006_patch_completar_recurrente_genera_la_siguiente(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    fecha_inicial = date.today()
    creado = client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={
            "nombre": "Limpiar canaletas",
            "recurrente": True,
            "periodicidad": "mensual",
            "fecha_estimada": fecha_inicial.isoformat(),
        },
        headers=_bearer(usuario_id),
    )
    item_id = creado.json()["id"]

    resp = client.patch(
        f"/casas/{casa.id}/mantenimiento/{item_id}",
        json={"estado": "completado"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["estado"] == "completado"

    listado = client.get(f"/casas/{casa.id}/mantenimiento", headers=_bearer(usuario_id)).json()
    assert len(listado) == 2
    nueva = next(i for i in listado if i["id"] != item_id)
    assert nueva["estado"] == "pendiente"
    assert nueva["fecha_estimada"] == (fecha_inicial + timedelta(days=30)).isoformat()


def test_tc007_patch_completar_antes_de_tiempo_responde_409(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    fecha_inicial = date.today()
    creado = client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={
            "nombre": "Limpiar canaletas",
            "recurrente": True,
            "periodicidad": "mensual",
            "fecha_estimada": fecha_inicial.isoformat(),
        },
        headers=_bearer(usuario_id),
    )
    item_id = creado.json()["id"]
    client.patch(
        f"/casas/{casa.id}/mantenimiento/{item_id}",
        json={"estado": "completado"},
        headers=_bearer(usuario_id),
    )
    listado = client.get(f"/casas/{casa.id}/mantenimiento", headers=_bearer(usuario_id)).json()
    nueva_id = next(i["id"] for i in listado if i["id"] != item_id)

    resp = client.patch(
        f"/casas/{casa.id}/mantenimiento/{nueva_id}",
        json={"estado": "completado"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 409


def test_patch_item_inexistente_responde_404(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.patch(
        f"/casas/{casa.id}/mantenimiento/{uuid.uuid4()}",
        json={"estado": "completado"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 404


def test_post_sin_jwt_devuelve_401(client):
    casa, _usuario_id, _admin_id = _crear_casa_directo()
    resp = client.post(f"/casas/{casa.id}/mantenimiento", json={"nombre": "Pintar el living"})
    assert resp.status_code == 401


def test_usuario_no_miembro_de_la_casa_recibe_403(client):
    casa, _usuario_id, _admin_id = _crear_casa_directo()
    usuario_ajeno = uuid.uuid4()

    resp = client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={"nombre": "Pintar el living"},
        headers=_bearer(usuario_ajeno),
    )
    assert resp.status_code == 403


def test_dashboard_incluye_mantenimiento_con_alerta(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={
            "nombre": "Arreglar el reflector",
            "fecha_estimada": (date.today() + timedelta(days=5)).isoformat(),
        },
        headers=_bearer(usuario_id),
    )
    client.post(
        f"/casas/{casa.id}/mantenimiento",
        json={
            "nombre": "Cambiar filtro de aire",
            "fecha_estimada": (date.today() + timedelta(days=20)).isoformat(),
        },
        headers=_bearer(usuario_id),
    )

    resp = client.get(f"/casas/{casa.id}/inicio", headers=_bearer(usuario_id))
    assert resp.status_code == 200, resp.text
    alertas = resp.json()["mantenimientoConAlerta"]
    assert len(alertas) == 1
    assert alertas[0]["nombre"] == "Arreglar el reflector"
