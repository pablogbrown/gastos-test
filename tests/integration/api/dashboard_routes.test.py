"""T3 — API Routes: contrato HTTP de dashboard y actividad.

Cubre que `GET /casas/{id}/inicio` y `GET /casas/{id}/actividad`
responden 200 con la estructura esperada, incluso sobre una casa sin
gastos ni tareas (TC-002), 404 sobre una casa inexistente, y la
migración a JWT de `usuarios-auth` (reemplaza `X-Usuario-Id`).
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
from src.db.models.usuario import Usuario
from src.services.auth_service import emitir_token
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
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email), y las rutas requieren JWT.
    "0005_usuarios",
    # 0009 (spec `gastos-suscripcion-mensual`): `listar_gastos` (llamado
    # por `GET /inicio` vía `armar_dashboard`) ahora dispara
    # `suscripcion_service.generar_gastos_pendientes` como primera línea,
    # que requiere la tabla `suscripciones`.
    "0009_suscripciones",
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
    "suscripcion_service",
)


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
    for nombre in _MIGRACIONES:
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for servicio in _SERVICIOS_CON_SESSION:
        monkeypatch.setattr(f"src.services.{servicio}.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(dashboard_router)
    client = TestClient(app)
    client._session_factory = TestSession
    return client


def _crear_casa_directo(nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    casa = crear_casa(nombre, usuario_id)
    admin_id = casa.miembros[0].id
    return casa, usuario_id, admin_id


def test_inicio_de_casa_vacia_responde_200_con_secciones_vacias(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.get(f"/casas/{casa.id}/inicio", headers=_bearer(usuario_id))

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["miembros"]) == 1
    assert body["gastosRecientes"] == []
    assert body["tareasPendientes"] == []
    assert body["tareasCompletadasRecientes"] == []
    assert body["ranking"] == []


def test_inicio_sin_jwt_devuelve_401(client):
    casa, _usuario_id, _admin_id = _crear_casa_directo()
    resp = client.get(f"/casas/{casa.id}/inicio")
    assert resp.status_code == 401


def test_inicio_de_casa_inexistente_devuelve_404(client):
    resp = client.get(
        f"/casas/{uuid.uuid4()}/inicio", headers=_bearer(uuid.uuid4())
    )
    assert resp.status_code == 404


def test_usuario_no_miembro_de_la_casa_recibe_403(client):
    """TC-009 (`usuarios-auth`)."""
    casa, _usuario_id, _admin_id = _crear_casa_directo()
    usuario_ajeno = uuid.uuid4()

    resp = client.get(f"/casas/{casa.id}/inicio", headers=_bearer(usuario_ajeno))
    assert resp.status_code == 403


def test_inicio_de_casa_refleja_gastos_tareas_y_ranking(client):
    casa, usuario_id, admin_id = _crear_casa_directo()
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
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

    resp = client.get(f"/casas/{casa.id}/inicio", headers=_bearer(usuario_id))

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["gastosRecientes"]) == 1
    assert len(body["tareasCompletadasRecientes"]) == 1
    assert body["ranking"][0]["miembroId"] == str(ana.id)
    assert body["ranking"][0]["puntos"] == 8


def test_actividad_de_casa_vacia_responde_200_lista_vacia(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.get(f"/casas/{casa.id}/actividad", headers=_bearer(usuario_id))

    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_actividad_de_casa_inexistente_devuelve_404(client):
    resp = client.get(
        f"/casas/{uuid.uuid4()}/actividad", headers=_bearer(uuid.uuid4())
    )
    assert resp.status_code == 404


def test_actividad_lista_eventos_de_mas_reciente_a_mas_antiguo(client):
    casa, usuario_id, admin_id = _crear_casa_directo()
    crear_tarea(casa.id, "Tarea 1", 1, actor=admin_id)
    crear_tarea(casa.id, "Tarea 2", 2, actor=admin_id)

    resp = client.get(f"/casas/{casa.id}/actividad", headers=_bearer(usuario_id))

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body) == 2
    fechas = [entrada["fecha"] for entrada in body]
    assert fechas == sorted(fechas, reverse=True)
