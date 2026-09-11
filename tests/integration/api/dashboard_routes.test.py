"""T3 — API Routes: contrato HTTP de dashboard y actividad.

Cubre que `GET /casas/{id}/inicio` y `GET /casas/{id}/actividad`
responden 200 con la estructura esperada, incluso sobre una casa sin
gastos ni tareas (TC-002), y 404 sobre una casa inexistente.
"""
import importlib
import uuid
from datetime import date
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.dashboard import dashboard_router
from src.services.casa_service import crear_casa
from src.services.categoria_service import crear_categoria
from src.services.gasto_service import registrar_gasto
from src.services.miembro_service import agregar_miembro
from src.services.tarea_service import completar_tarea, crear_tarea

_MIGRACIONES = (
    "0001_casas_miembros",
    "0002_gastos",
    "0003_tareas",
    "0004_historial_actividad",
)
_SERVICIOS_CON_SESSION = (
    "casa_service",
    "miembro_service",
    "categoria_service",
    "gasto_service",
    "tarea_service",
    "ranking_service",
    "balance_service",
    "actividad_service",
)


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    for nombre in _MIGRACIONES:
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for servicio in _SERVICIOS_CON_SESSION:
        monkeypatch.setattr(f"src.services.{servicio}.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(dashboard_router)
    return TestClient(app)


def _crear_casa_directo(nombre="Casa Brown"):
    admin_id = uuid.uuid4()
    casa = crear_casa(nombre, admin_id)
    return casa, admin_id


def test_inicio_de_casa_vacia_responde_200_con_secciones_vacias(client):
    casa, admin_id = _crear_casa_directo()

    resp = client.get(f"/casas/{casa.id}/inicio", headers={"X-Usuario-Id": str(admin_id)})

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["miembros"]) == 1
    assert body["gastosRecientes"] == []
    assert body["tareasPendientes"] == []
    assert body["tareasCompletadasRecientes"] == []
    assert body["ranking"] == []


def test_inicio_de_casa_inexistente_devuelve_404(client):
    resp = client.get(
        f"/casas/{uuid.uuid4()}/inicio", headers={"X-Usuario-Id": str(uuid.uuid4())}
    )
    assert resp.status_code == 404


def test_inicio_de_casa_refleja_gastos_tareas_y_ranking(client):
    casa, admin_id = _crear_casa_directo()
    ana = agregar_miembro(casa.id, "Ana", "ANA1", admin_id)
    categoria = crear_categoria(casa.id, "Supermercado", admin_id)
    registrar_gasto(
        casa.id,
        "Compra semanal",
        Decimal("10000.00"),
        date(2026, 1, 1),
        categoria.id,
        admin_id,
        admin_id,
    )
    tarea = crear_tarea(casa.id, "Lavar los platos", 8, actor=admin_id)
    completar_tarea(tarea.id, ana.id, ana.id)

    resp = client.get(f"/casas/{casa.id}/inicio", headers={"X-Usuario-Id": str(admin_id)})

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["gastosRecientes"]) == 1
    assert len(body["tareasCompletadasRecientes"]) == 1
    assert body["ranking"][0]["miembroId"] == str(ana.id)
    assert body["ranking"][0]["puntos"] == 8


def test_actividad_de_casa_vacia_responde_200_lista_vacia(client):
    casa, admin_id = _crear_casa_directo()

    resp = client.get(f"/casas/{casa.id}/actividad", headers={"X-Usuario-Id": str(admin_id)})

    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_actividad_de_casa_inexistente_devuelve_404(client):
    resp = client.get(
        f"/casas/{uuid.uuid4()}/actividad", headers={"X-Usuario-Id": str(uuid.uuid4())}
    )
    assert resp.status_code == 404


def test_actividad_lista_eventos_de_mas_reciente_a_mas_antiguo(client):
    casa, admin_id = _crear_casa_directo()
    crear_tarea(casa.id, "Tarea 1", 1, actor=admin_id)
    crear_tarea(casa.id, "Tarea 2", 2, actor=admin_id)

    resp = client.get(f"/casas/{casa.id}/actividad", headers={"X-Usuario-Id": str(admin_id)})

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body) == 2
    fechas = [entrada["fecha"] for entrada in body]
    assert fechas == sorted(fechas, reverse=True)
