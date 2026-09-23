"""T3 (spec `tienda-accesorios`) — API Routes: contrato HTTP de la
tienda de accesorios.

Cubre las 5 rutas del contrato de `spec.md` (anidadas bajo
`/casas/{casa_id}/miembros/{miembro_id}/...` — ver Judgment de
`tienda.py`): `GET .../accesorios/catalogo`, `GET .../accesorios`,
`POST .../accesorios/{accesorio_id}/comprar` (200/402/404/409),
`PUT .../accesorios/equipar` (200/403), `DELETE .../accesorios/{slot}/equipado`
(204). Done When de T3: las 5 rutas responden con los códigos esperados.
"""
import importlib
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.tienda import tienda_router
from src.db.models.accesorio_avatar import AccesorioAvatar
from src.db.models.avatar_personaje import AvatarPersonaje
from src.db.models.miembro_avatar_seleccionado import MiembroAvatarSeleccionado
from src.db.models.usuario import Usuario
from src.services.auth_service import emitir_token
from src.services.avatar_service import otorgar_creditos
from src.services.casa_service import crear_casa
from src.services.miembro_service import agregar_miembro


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
        "0004_historial_actividad",
        "0005_usuarios",
        "0021_creditos",
        "0022_avatar_catalogo",
        "0023_avatar_seleccionado",
        "0024_accesorio_catalogo",
        "0025_accesorio_comprado",
        "0026_accesorio_equipado",
    ):
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for servicio in ("casa_service", "miembro_service", "avatar_service", "tienda_service", "actividad_service"):
        monkeypatch.setattr(f"src.services.{servicio}.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(tienda_router)
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


def _insertar_accesorio(session_factory, **overrides):
    accesorio_id = uuid.uuid4()
    fila = {
        "id": accesorio_id,
        "nombre": "Accesorio de prueba",
        "slot": "cabeza",
        "rareza": "común",
        "precio_creditos": 10,
        "especie_compatible": "ambos",
        "asset_overlay_url": "https://assets.lottiefiles.com/packages/lf20_overlay_prueba.json",
        "disponible_desde": None,
        "disponible_hasta": None,
    }
    fila.update(overrides)
    session = session_factory()
    try:
        session.execute(insert(AccesorioAvatar.__table__), [fila])
        session.commit()
    finally:
        session.close()
    return accesorio_id


def test_get_catalogo_devuelve_200_con_los_campos_del_contrato(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)

    resp = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/catalogo",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) > 0
    assert "slot" in resp.json()[0]


def test_get_inventario_devuelve_200_vacio_sin_compras(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)

    resp = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_post_comprar_con_saldo_suficiente_devuelve_200_y_agrega_al_inventario(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    otorgar_creditos(casa.id, ana.id, 50, motivo="tarea_completada")
    accesorio_id = _insertar_accesorio(client._session_factory, precio_creditos=20)

    resp = client.post(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/{accesorio_id}/comprar",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text

    resp_inventario = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios",
        headers=_bearer(ana_usuario.id),
    )
    assert any(a["id"] == str(accesorio_id) for a in resp_inventario.json())


def test_post_comprar_con_saldo_insuficiente_devuelve_402(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    accesorio_id = _insertar_accesorio(client._session_factory, precio_creditos=20)

    resp = client.post(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/{accesorio_id}/comprar",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 402, resp.text


def test_post_comprar_dos_veces_devuelve_409_la_segunda_vez(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    otorgar_creditos(casa.id, ana.id, 100, motivo="tarea_completada")
    accesorio_id = _insertar_accesorio(client._session_factory, precio_creditos=20)

    client.post(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/{accesorio_id}/comprar",
        headers=_bearer(ana_usuario.id),
    )
    resp = client.post(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/{accesorio_id}/comprar",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 409, resp.text


def test_post_comprar_de_otro_miembro_devuelve_403(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    accesorio_id = _insertar_accesorio(client._session_factory, precio_creditos=20)

    resp = client.post(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/{accesorio_id}/comprar",
        headers=_bearer(usuario_admin_id),
    )
    assert resp.status_code == 403, resp.text


def test_put_equipar_un_accesorio_comprado_devuelve_200(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    otorgar_creditos(casa.id, ana.id, 100, motivo="tarea_completada")
    accesorio_id = _insertar_accesorio(client._session_factory, precio_creditos=20)
    client.post(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/{accesorio_id}/comprar",
        headers=_bearer(ana_usuario.id),
    )

    resp = client.put(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/equipar",
        json={"accesorio_id": str(accesorio_id)},
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == str(accesorio_id)


def test_put_equipar_un_accesorio_no_comprado_devuelve_403(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    accesorio_id = _insertar_accesorio(client._session_factory, precio_creditos=20)

    resp = client.put(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/equipar",
        json={"accesorio_id": str(accesorio_id)},
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 403, resp.text


def test_get_equipados_devuelve_200_vacio_sin_nada_equipado(client):
    """Spec `perfil-avatar-ui`, REQ-001 ([S003] de `tienda-accesorios`
    resuelto acá): ruta nueva, no contemplada en el contrato original de
    esta spec."""
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)

    resp = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/equipados",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_get_equipados_devuelve_el_detalle_del_accesorio_tras_equipar(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    otorgar_creditos(casa.id, ana.id, 100, motivo="tarea_completada")
    accesorio_id = _insertar_accesorio(client._session_factory, slot="cabeza", precio_creditos=20)
    client.post(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/{accesorio_id}/comprar",
        headers=_bearer(ana_usuario.id),
    )
    client.put(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/equipar",
        json={"accesorio_id": str(accesorio_id)},
        headers=_bearer(ana_usuario.id),
    )

    resp = client.get(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/equipados",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 200, resp.text
    assert [a["id"] for a in resp.json()] == [str(accesorio_id)]


def test_delete_equipado_desequipa_el_slot_devuelve_204(client):
    casa, usuario_admin_id, admin_id, ana, ana_usuario = _casa_con_miembro(client._session_factory)
    otorgar_creditos(casa.id, ana.id, 100, motivo="tarea_completada")
    accesorio_id = _insertar_accesorio(client._session_factory, slot="cuello", precio_creditos=20)
    client.post(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/{accesorio_id}/comprar",
        headers=_bearer(ana_usuario.id),
    )
    client.put(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/equipar",
        json={"accesorio_id": str(accesorio_id)},
        headers=_bearer(ana_usuario.id),
    )

    resp = client.delete(
        f"/casas/{casa.id}/miembros/{ana.id}/accesorios/cuello/equipado",
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 204, resp.text
