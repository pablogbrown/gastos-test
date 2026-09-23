"""T3 (spec `avatares-economia`) — API Routes: contrato HTTP de
avatares/créditos.

Cubre las 4 rutas del contrato de `spec.md` (anidadas bajo
`/casas/{casa_id}/miembros/{miembro_id}/...` — ver Judgment de
`avatares.py`): `GET .../creditos`, `GET .../avatares-disponibles`,
`GET .../avatar`, `PUT .../avatar` (200/403/404).
"""
import importlib
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.avatares import avatares_router
from src.db.models.usuario import Usuario
from src.services.auth_service import emitir_token
from src.services.casa_service import crear_casa
from src.services.miembro_service import agregar_miembro
from src.services.tarea_service import completar_tarea, crear_tarea


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
    for nombre in (
        "0001_casas_miembros",
        "0003_tareas",
        "0004_historial_actividad",
        "0005_usuarios",
        "0020_gamificacion",
        "0021_creditos",
        "0022_avatar_catalogo",
        "0023_avatar_seleccionado",
    ):
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for servicio in (
        "casa_service",
        "miembro_service",
        "tarea_service",
        "ranking_service",
        "actividad_service",
        "avatar_service",
        # `completar_tarea` también dispara `logro_service.evaluar_logros`
        # (spec `gamificacion-puntos`, ya existente) — sin mockear esto,
        # su propia sesión sin mockear cae sobre el engine global por
        # default del proceso, que no tiene ninguna tabla migrada.
        "logro_service",
    ):
        monkeypatch.setattr(f"src.services.{servicio}.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(avatares_router)
    test_client = TestClient(app)
    test_client._session_factory = TestSession
    return test_client


def _casa_con_miembro(session_factory):
    usuario_admin_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_admin_id)
    admin_id = casa.miembros[0].id
    ana_usuario = _crear_usuario_de_prueba(session_factory, "ana@example.com")
    ana = agregar_miembro(casa.id, "Ana", "ANA1", ana_usuario.email, admin_id)
    return casa, usuario_admin_id, admin_id, ana, ana_usuario


def test_get_creditos_devuelve_saldo_cero_sin_transacciones(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)

    resp = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/creditos",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"saldo": 0}


def test_get_creditos_refleja_saldo_tras_completar_tarea(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    tarea = crear_tarea(casa.id, "Sacar la basura", 15, actor=admin_id)
    completar_tarea(tarea.id, ana.id, ana.id)

    resp = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/creditos",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"saldo": 15}


def test_get_avatares_disponibles_solo_expone_razas_del_nivel_actual(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)

    resp = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/avatares-disponibles",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    razas = resp.json()
    assert len(razas) > 0
    assert all(raza["nivel_requerido"] == "Novato" for raza in razas)


def test_get_avatares_catalogo_incluye_razas_bloqueadas_para_el_nivel_actual(client):
    """Spec `perfil-avatar-ui`, REQ-002/TC-004 — ruta nueva, no expuesta
    por `avatares-economia` (esa spec solo expone `avatares-disponibles`,
    ya filtrado por nivel). Un miembro Novato debe ver en el catálogo
    completo razas de nivel superior (bloqueadas), no solo las suyas."""
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)

    resp = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/avatares-catalogo",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    razas = resp.json()
    niveles = {raza["nivel_requerido"] for raza in razas}
    assert "Novato" in niveles
    assert len(niveles) > 1, "el catálogo completo debe incluir niveles superiores al actual (bloqueados)"


def test_get_avatar_sin_seleccion_devuelve_null(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)

    resp = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/avatar",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() is None


def test_put_avatar_selecciona_una_raza_desbloqueada(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    disponibles = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/avatares-disponibles",
        headers=_bearer(ana_usuario.id),
    ).json()
    raza = disponibles[0]

    resp = client.put(
        f"/casas/{casa.id}/miembros/{ana.id}/avatar",
        json={"avatar_personaje_id": raza["id"]},
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == raza["id"]

    resp_get = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/avatar",
        headers=_bearer(ana_usuario.id),
    )
    assert resp_get.json()["id"] == raza["id"]


def test_put_avatar_con_raza_de_nivel_superior_devuelve_403(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)

    session = client._session_factory()
    try:
        from src.db.models.avatar_personaje import AvatarPersonaje

        raza_activo = (
            session.query(AvatarPersonaje)
            .filter(AvatarPersonaje.nivel_requerido == "Activo")
            .first()
        )
    finally:
        session.close()

    resp = client.put(
        f"/casas/{casa.id}/miembros/{ana.id}/avatar",
        json={"avatar_personaje_id": str(raza_activo.id)},
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 403, resp.text


def test_put_avatar_de_otro_miembro_devuelve_403(client):
    """El PUT es self-service: ni siquiera un Administrador puede elegir
    el avatar de otro miembro en su nombre (a diferencia de
    `completar_tarea`) — Judgment de `avatares.py`."""
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    disponibles = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/avatares-disponibles",
        headers=_bearer(ana_usuario.id),
    ).json()
    raza = disponibles[0]

    resp = client.put(
        f"/casas/{casa.id}/miembros/{ana.id}/avatar",
        json={"avatar_personaje_id": raza["id"]},
        headers=_bearer(usuario_admin_id),
    )
    assert resp.status_code == 403, resp.text
