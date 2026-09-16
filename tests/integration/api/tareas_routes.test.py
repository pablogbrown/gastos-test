"""T3 — API Routes: contrato HTTP de tareas/ranking/historial.

Cubre TC-010 (historial conserva miembros desactivados), los contratos
400 (crear sin nombre/puntos) y 409 (completar una tarea ya completada),
y la migración a JWT de `usuarios-auth` (reemplaza `X-Usuario-Id`).
"""
import importlib
import uuid
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.tareas import tareas_router
from src.db.models.usuario import Usuario
from src.services.auth_service import emitir_token
from src.services.casa_service import crear_casa
from src.services.miembro_service import agregar_miembro, desactivar_miembro


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
    migracion_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migracion_tareas = importlib.import_module("src.db.migrations.0003_tareas")
    # 0004 (spec `dashboard-actividad`): `crear_tarea`/`completar_tarea`
    # disparan un hook a `actividad_service.registrar_actividad`, que
    # requiere la tabla `historial_actividad`.
    migracion_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email), y las rutas requieren JWT.
    migracion_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    migracion_casas.upgrade(engine)
    migracion_tareas.upgrade(engine)
    migracion_actividad.upgrade(engine)
    migracion_usuarios.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.tarea_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.ranking_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(tareas_router)
    client = TestClient(app)
    client._session_factory = TestSession
    return client


def _casa_con_miembro(session_factory, nombre_miembro="Ana", identificacion="ANA1"):
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    miembro_usuario = _crear_usuario_de_prueba(session_factory, "ana@example.com")
    miembro = agregar_miembro(casa.id, nombre_miembro, identificacion, miembro_usuario.email, admin_id)
    return casa, usuario_id, miembro


def _crear_tarea(client, casa_id, usuario_id, **overrides):
    body = {"nombre": "Sacar la basura", "puntos": 5}
    body.update(overrides)
    resp = client.post(f"/casas/{casa_id}/tareas", json=body, headers=_bearer(usuario_id))
    assert resp.status_code == 201, resp.text
    return resp.json()


def _completar(client, casa_id, tarea_id, usuario_id):
    return client.patch(
        f"/casas/{casa_id}/tareas/{tarea_id}",
        json={"estado": "completada"},
        headers=_bearer(usuario_id),
    )


def test_crear_tarea_sin_jwt_devuelve_401(client):
    casa, _usuario_id, _miembro = _casa_con_miembro(client._session_factory)

    resp = client.post(f"/casas/{casa.id}/tareas", json={"nombre": "Lavar", "puntos": 5})
    assert resp.status_code == 401


def test_crear_tarea_sin_nombre_devuelve_400(client):
    casa, usuario_id, _miembro = _casa_con_miembro(client._session_factory)

    resp = client.post(
        f"/casas/{casa.id}/tareas",
        json={"nombre": "", "puntos": 5},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_crear_tarea_sin_puntos_devuelve_400(client):
    casa, usuario_id, _miembro = _casa_con_miembro(client._session_factory)

    resp = client.post(
        f"/casas/{casa.id}/tareas",
        json={"nombre": "Lavar los platos"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_crear_tarea_devuelve_201_con_estado_pendiente(client):
    casa, usuario_id, _miembro = _casa_con_miembro(client._session_factory)

    tarea = _crear_tarea(client, casa.id, usuario_id, nombre="Lavar los platos", puntos=5)

    assert tarea["estado"] == "pendiente"
    assert tarea["nombre"] == "Lavar los platos"


def test_usuario_no_miembro_de_la_casa_recibe_403(client):
    """TC-009 (`usuarios-auth`)."""
    casa, _usuario_id, _miembro = _casa_con_miembro(client._session_factory)
    usuario_ajeno = uuid.uuid4()

    resp = client.get(f"/casas/{casa.id}/tareas", headers=_bearer(usuario_ajeno))
    assert resp.status_code == 403


def test_completar_tarea_ya_completada_devuelve_409(client):
    casa, usuario_id, miembro = _casa_con_miembro(client._session_factory)
    tarea = _crear_tarea(client, casa.id, usuario_id)

    # El actor que completa la tarea es el propio `miembro` (Ana) —
    # necesita su propio JWT, no el del admin. `agregar_miembro` vinculó
    # a `miembro` al Usuario "ana@example.com"; se resuelve su id real
    # consultando el Miembro directamente (no queda expuesto por HTTP en
    # este flujo simplificado de test).
    primero = _completar(client, casa.id, tarea["id"], _usuario_id_de(miembro))
    assert primero.status_code == 200, primero.text

    segundo = _completar(client, casa.id, tarea["id"], _usuario_id_de(miembro))
    assert segundo.status_code == 409


def _usuario_id_de(miembro):
    return miembro.usuario_id


def test_ranking_refleja_puntos_tras_completar(client):
    casa, usuario_id, miembro = _casa_con_miembro(client._session_factory)
    tarea = _crear_tarea(client, casa.id, usuario_id, puntos=10)

    _completar(client, casa.id, tarea["id"], _usuario_id_de(miembro))

    resp = client.get(f"/casas/{casa.id}/ranking", headers=_bearer(usuario_id))
    assert resp.status_code == 200
    entrada = next(fila for fila in resp.json() if fila["miembroId"] == str(miembro.id))
    assert entrada["puntos"] == 10


def test_historial_conserva_registros_de_miembros_desactivados(client):
    casa, usuario_id, miembro = _casa_con_miembro(client._session_factory)
    admin_id = casa.miembros[0].id
    tarea = _crear_tarea(client, casa.id, usuario_id, puntos=6)
    _completar(client, casa.id, tarea["id"], _usuario_id_de(miembro))

    desactivar_miembro(casa.id, miembro.id, admin_id)

    resp = client.get(f"/casas/{casa.id}/tareas/historial", headers=_bearer(usuario_id))
    assert resp.status_code == 200
    historial = resp.json()
    assert any(registro["miembro_id"] == str(miembro.id) for registro in historial)
    assert any(registro["puntos_obtenidos"] == 6 for registro in historial)


def test_tarea_recurrente_completada_genera_nueva_instancia_via_api(client):
    casa, usuario_id, miembro = _casa_con_miembro(client._session_factory)
    tarea = _crear_tarea(
        client,
        casa.id,
        usuario_id,
        puntos=3,
        recurrente=True,
        frecuencia="diaria",
        fechaPrevista=date.today().isoformat(),
    )

    _completar(client, casa.id, tarea["id"], _usuario_id_de(miembro))

    resp = client.get(
        f"/casas/{casa.id}/tareas?estado=pendiente", headers=_bearer(usuario_id)
    )
    assert resp.status_code == 200
    pendientes = resp.json()
    assert any(
        t["nombre"] == "Sacar la basura" and t["id"] != tarea["id"] for t in pendientes
    )


def test_completar_tarea_recurrente_antes_de_su_fecha_prevista_devuelve_409(client):
    """Regresión (reportado en vivo): completar una tarea diaria varias
    veces el mismo día generaba una nueva instancia inmediatamente
    completable, sin ningún límite real de frecuencia."""
    casa, usuario_id, miembro = _casa_con_miembro(client._session_factory)
    tarea = _crear_tarea(
        client,
        casa.id,
        usuario_id,
        nombre="Lavar los platos",
        puntos=1,
        recurrente=True,
        frecuencia="diaria",
        fechaPrevista=date.today().isoformat(),
    )
    _completar(client, casa.id, tarea["id"], _usuario_id_de(miembro))

    resp = client.get(
        f"/casas/{casa.id}/tareas?estado=pendiente", headers=_bearer(usuario_id)
    )
    nueva = next(t for t in resp.json() if t["id"] != tarea["id"])

    resp = _completar(client, casa.id, nueva["id"], _usuario_id_de(miembro))
    assert resp.status_code == 409


def test_completar_tarea_inexistente_devuelve_404(client):
    casa, usuario_id, miembro = _casa_con_miembro(client._session_factory)

    resp = _completar(client, casa.id, uuid.uuid4(), _usuario_id_de(miembro))
    assert resp.status_code == 404
