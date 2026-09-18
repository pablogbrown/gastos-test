"""T3 — API Routes: contrato HTTP de casas/miembros.

Cubre TC-005/TC-006/TC-009 (`usuarios-auth`: JWT reemplaza `X-Usuario-Id`)
y preserva la cobertura original de `casas-miembros` (403 sin permisos,
200 admin sin restricción, comportamiento del guard de membresía).
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
from src.db.models.usuario import Usuario
from src.services.auth_service import emitir_token


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
    importlib.import_module("src.db.migrations.0001_casas_miembros").upgrade(engine)
    # 0004 (spec `fix-historial-desactivacion-miembro`): agregar/desactivar
    # miembro ahora registran actividad, que requiere esta tabla.
    importlib.import_module("src.db.migrations.0004_historial_actividad").upgrade(engine)
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email) para vincular al nuevo Miembro.
    importlib.import_module("src.db.migrations.0005_usuarios").upgrade(engine)
    # 0020 (spec `gamificacion-puntos`): `actualizar_meta_puntos` escribe
    # `casas.meta_puntos_mensual`.
    importlib.import_module("src.db.migrations.0020_gamificacion").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    client = TestClient(app)
    client._session_factory = TestSession  # para crear Usuarios reales desde los tests
    return client


def _crear_casa(client, nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    resp = client.post("/casas", json={"nombre": nombre}, headers=_bearer(usuario_id))
    assert resp.status_code == 201, resp.text
    body = resp.json()
    admin_id = body["miembros"][0]["id"]
    return body, usuario_id, admin_id


def test_crear_casa_devuelve_201_con_admin_incluido(client):
    body, usuario_id, admin_id = _crear_casa(client)
    assert body["nombre"] == "Casa Brown"
    assert len(body["miembros"]) == 1
    # Spec `usuarios-auth`: el `Miembro.id` ya no es el `usuario_id` del
    # token — solo el `Miembro.usuario_id` (no expuesto en `MiembroOut`)
    # lo vincula a la identidad real.
    assert body["miembros"][0]["id"] == admin_id
    assert body["miembros"][0]["rol"] == "admin"


def test_crear_casa_sin_jwt_devuelve_401(client):
    resp = client.post("/casas", json={"nombre": "Casa Brown"})
    assert resp.status_code == 401


def test_crear_casa_con_jwt_invalido_devuelve_401(client):
    resp = client.post(
        "/casas",
        json={"nombre": "Casa Brown"},
        headers={"Authorization": "Bearer esto-no-es-un-jwt"},
    )
    assert resp.status_code == 401


def test_crear_casa_sin_nombre_devuelve_400(client):
    resp = client.post(
        "/casas", json={"nombre": ""}, headers=_bearer(uuid.uuid4())
    )
    assert resp.status_code == 400


def test_operar_sobre_casa_sin_ser_miembro_devuelve_403(client):
    """TC-009: un Usuario autenticado que no es miembro de la Casa X no
    puede operar sobre ella, incluso con un JWT válido de otro usuario
    legítimo."""
    casa, _usuario_id, _admin_id = _crear_casa(client)
    usuario_ajeno = uuid.uuid4()

    resp = client.get(f"/casas/{casa['id']}/miembros", headers=_bearer(usuario_ajeno))
    assert resp.status_code == 403


def test_operar_sobre_casa_inexistente_devuelve_404(client):
    resp = client.get(f"/casas/{uuid.uuid4()}/miembros", headers=_bearer(uuid.uuid4()))
    assert resp.status_code == 404


def test_miembro_sin_permisos_recibe_403_al_agregar_miembro(client):
    casa, _usuario_id, _admin_id = _crear_casa(client)
    casa_id = casa["id"]
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")

    ana_resp = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(_usuario_id),
    )
    assert ana_resp.status_code == 201, ana_resp.text

    bruno_usuario = _crear_usuario_de_prueba(client._session_factory, "bruno@example.com")
    resp = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Bruno", "identificacion": "BRU1", "email": bruno_usuario.email},
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 403


def test_admin_consulta_listado_completo_de_miembros_sin_restriccion(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    casa_id = casa["id"]
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")
    client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    )

    resp = client.get(f"/casas/{casa_id}/miembros", headers=_bearer(usuario_id))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_listado_de_miembros_incluye_usuario_id(client):
    """TC-001 (spec `resolver-rol-usuario-en-casa`, REQ-001): cada objeto
    del listado de miembros incluye `usuario_id` — necesario para que el
    frontend cruce "cuál es mi Miembro en esta casa" contra el `sub` del
    JWT propio."""
    casa, usuario_id, admin_id = _crear_casa(client)
    casa_id = casa["id"]
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")
    client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    )

    resp = client.get(f"/casas/{casa_id}/miembros", headers=_bearer(usuario_id))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    por_id = {m["id"]: m for m in body}
    assert por_id[admin_id]["usuario_id"] == str(usuario_id)
    ana_miembro = next(m for m in body if m["id"] != admin_id)
    assert ana_miembro["usuario_id"] == str(ana_usuario.id)


def test_agregar_miembro_con_email_de_usuario_inexistente_crea_membresia_pendiente(client):
    """Spec `invitar-miembro-pendiente` (REQ-001): reemplaza el 404 previo
    — ahora la API responde 201 igual, con `usuario_id: null` (queda
    "pendiente" hasta que esa persona se registre con ese email)."""
    casa, usuario_id, _admin_id = _crear_casa(client)
    resp = client.post(
        f"/casas/{casa['id']}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": "no-registrado@example.com"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["usuario_id"] is None


def test_desactivar_miembro_devuelve_200_y_activo_false(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    casa_id = casa["id"]
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")
    ana = client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    ).json()

    resp = client.patch(
        f"/casas/{casa_id}/miembros/{ana['id']}",
        json={"activo": False},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 200
    assert resp.json()["activo"] is False


def test_listar_casas_mias_devuelve_solo_las_casas_con_miembro_activo(client):
    usuario_id = uuid.uuid4()
    client.post("/casas", json={"nombre": "Casa Brown"}, headers=_bearer(usuario_id))
    client.post("/casas", json={"nombre": "Casa Verde"}, headers=_bearer(usuario_id))
    client.post("/casas", json={"nombre": "Casa de Otro"}, headers=_bearer(uuid.uuid4()))

    resp = client.get("/casas/mias", headers=_bearer(usuario_id))
    assert resp.status_code == 200
    nombres = {c["nombre"] for c in resp.json()}
    assert nombres == {"Casa Brown", "Casa Verde"}


def test_listar_casas_mias_sin_jwt_devuelve_401(client):
    resp = client.get("/casas/mias")
    assert resp.status_code == 401


def test_admin_puede_configurar_la_meta_de_puntos(client):
    """TC-006 (spec `gamificacion-puntos`), a nivel HTTP: un Administrador
    puede configurar `PATCH /casas/{id}/meta`."""
    body, usuario_id, _ = _crear_casa(client)
    casa_id = body["id"]

    resp = client.patch(
        f"/casas/{casa_id}/meta", json={"meta": 200}, headers=_bearer(usuario_id)
    )
    assert resp.status_code == 200
    assert resp.json()["meta_puntos_mensual"] == 200


def test_no_admin_no_puede_configurar_la_meta_de_puntos(client):
    body, usuario_id, admin_id = _crear_casa(client)
    casa_id = body["id"]
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")
    client.post(
        f"/casas/{casa_id}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    )

    resp = client.patch(
        f"/casas/{casa_id}/meta", json={"meta": 200}, headers=_bearer(ana_usuario.id)
    )
    assert resp.status_code == 403
