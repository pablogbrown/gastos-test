"""T3 — API Routes: contrato HTTP de tareas/ranking/historial.

Cubre TC-010 (historial conserva miembros desactivados) y los contratos
400 (crear sin nombre/puntos) y 409 (completar una tarea ya completada).
"""
import importlib
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.tareas import tareas_router
from src.services.casa_service import crear_casa
from src.services.miembro_service import agregar_miembro, desactivar_miembro


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    migracion_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migracion_tareas = importlib.import_module("src.db.migrations.0003_tareas")
    migracion_casas.upgrade(engine)
    migracion_tareas.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.ranking_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(tareas_router)
    return TestClient(app)


def _casa_con_miembro(nombre_miembro="Ana", identificacion="ANA1"):
    admin_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", admin_id)
    miembro = agregar_miembro(casa.id, nombre_miembro, identificacion, admin_id)
    return casa, admin_id, miembro


def _crear_tarea(client, casa_id, admin_id, **overrides):
    body = {"nombre": "Sacar la basura", "puntos": 5}
    body.update(overrides)
    resp = client.post(
        f"/casas/{casa_id}/tareas", json=body, headers={"X-Usuario-Id": str(admin_id)}
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _completar(client, casa_id, tarea_id, usuario_id):
    return client.patch(
        f"/casas/{casa_id}/tareas/{tarea_id}",
        json={"estado": "completada"},
        headers={"X-Usuario-Id": str(usuario_id)},
    )


def test_crear_tarea_sin_nombre_devuelve_400(client):
    casa, admin_id, _ = _casa_con_miembro()

    resp = client.post(
        f"/casas/{casa.id}/tareas",
        json={"nombre": "", "puntos": 5},
        headers={"X-Usuario-Id": str(admin_id)},
    )
    assert resp.status_code == 400


def test_crear_tarea_sin_puntos_devuelve_400(client):
    casa, admin_id, _ = _casa_con_miembro()

    resp = client.post(
        f"/casas/{casa.id}/tareas",
        json={"nombre": "Lavar los platos"},
        headers={"X-Usuario-Id": str(admin_id)},
    )
    assert resp.status_code == 400


def test_crear_tarea_devuelve_201_con_estado_pendiente(client):
    casa, admin_id, _ = _casa_con_miembro()

    tarea = _crear_tarea(client, casa.id, admin_id, nombre="Lavar los platos", puntos=5)

    assert tarea["estado"] == "pendiente"
    assert tarea["nombre"] == "Lavar los platos"


def test_completar_tarea_ya_completada_devuelve_409(client):
    casa, admin_id, miembro = _casa_con_miembro()
    tarea = _crear_tarea(client, casa.id, admin_id)

    primero = _completar(client, casa.id, tarea["id"], miembro.id)
    assert primero.status_code == 200, primero.text

    segundo = _completar(client, casa.id, tarea["id"], miembro.id)
    assert segundo.status_code == 409


def test_ranking_refleja_puntos_tras_completar(client):
    casa, admin_id, miembro = _casa_con_miembro()
    tarea = _crear_tarea(client, casa.id, admin_id, puntos=10)

    _completar(client, casa.id, tarea["id"], miembro.id)

    resp = client.get(f"/casas/{casa.id}/ranking", headers={"X-Usuario-Id": str(admin_id)})
    assert resp.status_code == 200
    entrada = next(fila for fila in resp.json() if fila["miembroId"] == str(miembro.id))
    assert entrada["puntos"] == 10


def test_historial_conserva_registros_de_miembros_desactivados(client):
    casa, admin_id, miembro = _casa_con_miembro()
    tarea = _crear_tarea(client, casa.id, admin_id, puntos=6)
    _completar(client, casa.id, tarea["id"], miembro.id)

    desactivar_miembro(casa.id, miembro.id, admin_id)

    resp = client.get(
        f"/casas/{casa.id}/tareas/historial", headers={"X-Usuario-Id": str(admin_id)}
    )
    assert resp.status_code == 200
    historial = resp.json()
    assert any(registro["miembro_id"] == str(miembro.id) for registro in historial)
    assert any(registro["puntos_obtenidos"] == 6 for registro in historial)


def test_tarea_recurrente_completada_genera_nueva_instancia_via_api(client):
    casa, admin_id, miembro = _casa_con_miembro()
    tarea = _crear_tarea(
        client, casa.id, admin_id, puntos=3, recurrente=True, frecuencia="diaria"
    )

    _completar(client, casa.id, tarea["id"], miembro.id)

    resp = client.get(
        f"/casas/{casa.id}/tareas?estado=pendiente", headers={"X-Usuario-Id": str(admin_id)}
    )
    assert resp.status_code == 200
    pendientes = resp.json()
    assert any(
        t["nombre"] == "Sacar la basura" and t["id"] != tarea["id"] for t in pendientes
    )


def test_completar_tarea_inexistente_devuelve_404(client):
    casa, admin_id, miembro = _casa_con_miembro()

    resp = _completar(client, casa.id, uuid.uuid4(), miembro.id)
    assert resp.status_code == 404
