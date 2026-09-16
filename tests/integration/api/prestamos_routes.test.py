"""T3 (spec `prestamos-entre-miembros`) — API Routes: contrato HTTP de
préstamos.

Cubre TC-001 a TC-005 a nivel HTTP (10-verify.md).
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

from src.api.routes.casas import casas_router
from src.api.routes.prestamos import prestamos_router
from src.db.models.usuario import Usuario
from src.services.auth_service import emitir_token
from src.services.casa_service import crear_casa
from src.services.miembro_service import agregar_miembro


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
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    migration_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    migration_prestamos = importlib.import_module("src.db.migrations.0014_prestamos")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)
    migration_prestamos.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.prestamo_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(prestamos_router)
    client = TestClient(app)
    client._session_factory = TestSession
    return client


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


def _crear_casa_con_dos_miembros(session_factory, nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    casa = crear_casa(nombre, usuario_id)
    admin_id = casa.miembros[0].id
    maca_usuario = _crear_usuario_de_prueba(session_factory, "maca@example.com")
    maca = agregar_miembro(casa.id, "Maca", "MACA1", maca_usuario.email, admin_id)
    return casa, usuario_id, admin_id, maca.id


def _payload_valido(prestamista_id, deudor_id):
    return {
        "prestamista_id": str(prestamista_id),
        "deudor_id": str(deudor_id),
        "importe": "50000.00",
        "moneda": "ARS",
        "fecha": date(2026, 9, 1).isoformat(),
        "descripcion": "Alquiler del auto",
    }


def test_tc001_post_crea_prestamo_pendiente_y_aparece_en_el_listado(client):
    casa, usuario_id, admin_id, maca_id = _crear_casa_con_dos_miembros(client._session_factory)

    resp = client.post(
        f"/casas/{casa.id}/prestamos",
        json=_payload_valido(admin_id, maca_id),
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["estado"] == "pendiente"
    assert body["prestamista_id"] == str(admin_id)
    assert body["deudor_id"] == str(maca_id)

    listado = client.get(f"/casas/{casa.id}/prestamos", headers=_bearer(usuario_id))
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["id"] == body["id"]


def test_tc002_prestamista_igual_a_deudor_responde_400(client):
    casa, usuario_id, admin_id, _maca_id = _crear_casa_con_dos_miembros(client._session_factory)

    payload = _payload_valido(admin_id, admin_id)
    resp = client.post(
        f"/casas/{casa.id}/prestamos", json=payload, headers=_bearer(usuario_id)
    )
    assert resp.status_code == 400


def test_tc003_moneda_invalida_responde_400(client):
    casa, usuario_id, admin_id, maca_id = _crear_casa_con_dos_miembros(client._session_factory)

    payload = _payload_valido(admin_id, maca_id)
    payload["moneda"] = "EUR"
    resp = client.post(
        f"/casas/{casa.id}/prestamos", json=payload, headers=_bearer(usuario_id)
    )
    assert resp.status_code == 400


def test_tc004_patch_cambia_estado_en_ambos_sentidos(client):
    casa, usuario_id, admin_id, maca_id = _crear_casa_con_dos_miembros(client._session_factory)
    creado = client.post(
        f"/casas/{casa.id}/prestamos",
        json=_payload_valido(admin_id, maca_id),
        headers=_bearer(usuario_id),
    )
    prestamo_id = creado.json()["id"]

    resp = client.patch(
        f"/casas/{casa.id}/prestamos/{prestamo_id}",
        json={"estado": "pagado"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["estado"] == "pagado"

    resp2 = client.patch(
        f"/casas/{casa.id}/prestamos/{prestamo_id}",
        json={"estado": "pendiente"},
        headers=_bearer(usuario_id),
    )
    assert resp2.status_code == 200
    assert resp2.json()["estado"] == "pendiente"


def test_tc005_listado_ordenado_por_fecha_descendente(client):
    casa, usuario_id, admin_id, maca_id = _crear_casa_con_dos_miembros(client._session_factory)

    payload_viejo = _payload_valido(admin_id, maca_id)
    payload_viejo["fecha"] = date(2026, 8, 1).isoformat()
    payload_nuevo = _payload_valido(admin_id, maca_id)
    payload_nuevo["fecha"] = date(2026, 9, 10).isoformat()

    client.post(f"/casas/{casa.id}/prestamos", json=payload_viejo, headers=_bearer(usuario_id))
    client.post(f"/casas/{casa.id}/prestamos", json=payload_nuevo, headers=_bearer(usuario_id))

    listado = client.get(f"/casas/{casa.id}/prestamos", headers=_bearer(usuario_id))
    fechas = [item["fecha"] for item in listado.json()]
    assert fechas == sorted(fechas, reverse=True)
