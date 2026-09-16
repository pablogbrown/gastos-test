"""T3 (spec `prestamos-confirmacion-mutua`) — API Routes: contrato HTTP
del endpoint de confirmación de préstamo.

Cubre TC-004, TC-005, TC-006, TC-007 a nivel HTTP (`10-verify.md`).
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
from src.db.models.miembro import Miembro
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


def _bearer_de_miembro(session_factory, miembro_id):
    session = session_factory()
    try:
        miembro = session.get(Miembro, miembro_id)
        return _bearer(miembro.usuario_id)
    finally:
        session.close()


def _crear_casa_con_tres_miembros(session_factory, nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    casa = crear_casa(nombre, usuario_id)
    admin_id = casa.miembros[0].id
    maca_usuario = _crear_usuario_de_prueba(session_factory, "maca@example.com")
    maca = agregar_miembro(casa.id, "Maca", "MACA1", maca_usuario.email, admin_id)
    bruno_usuario = _crear_usuario_de_prueba(session_factory, "bruno@example.com")
    bruno = agregar_miembro(casa.id, "Bruno", "BRU1", bruno_usuario.email, admin_id)
    return casa, usuario_id, admin_id, maca.id, bruno.id


def _payload_valido(prestamista_id, deudor_id):
    return {
        "prestamista_id": str(prestamista_id),
        "deudor_id": str(deudor_id),
        "importe": "50000.00",
        "moneda": "ARS",
        "fecha": date(2026, 9, 1).isoformat(),
        "descripcion": "Alquiler del auto",
    }


def _crear_prestamo(client, casa_id, usuario_id_actor, prestamista_id, deudor_id):
    resp = client.post(
        f"/casas/{casa_id}/prestamos",
        json=_payload_valido(prestamista_id, deudor_id),
        headers=_bearer(usuario_id_actor),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_tc004_tercero_no_puede_confirmar_responde_403(client):
    casa, usuario_id, admin_id, maca_id, bruno_id = _crear_casa_con_tres_miembros(
        client._session_factory
    )
    creado = _crear_prestamo(client, casa.id, usuario_id, admin_id, maca_id)

    resp = client.patch(
        f"/casas/{casa.id}/prestamos/{creado['id']}/confirmacion",
        json={"confirma": True},
        headers=_bearer_de_miembro(client._session_factory, bruno_id),
    )
    assert resp.status_code == 403


def test_tc005_ambas_partes_confirman_queda_confirmado(client):
    casa, usuario_id, admin_id, maca_id, _bruno_id = _crear_casa_con_tres_miembros(
        client._session_factory
    )
    creado = _crear_prestamo(client, casa.id, usuario_id, admin_id, maca_id)
    assert creado["estado_confirmacion"] == "pendiente_confirmacion"
    assert creado["confirmado_prestamista"] is True
    assert creado["confirmado_deudor"] is None

    resp = client.patch(
        f"/casas/{casa.id}/prestamos/{creado['id']}/confirmacion",
        json={"confirma": True},
        headers=_bearer_de_miembro(client._session_factory, maca_id),
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["confirmado_prestamista"] is True
    assert body["confirmado_deudor"] is True
    assert body["estado_confirmacion"] == "confirmado"


def test_tc006_una_parte_rechaza_responde_rechazado_permanente(client):
    casa, usuario_id, admin_id, maca_id, _bruno_id = _crear_casa_con_tres_miembros(
        client._session_factory
    )
    creado = _crear_prestamo(client, casa.id, usuario_id, admin_id, maca_id)

    resp = client.patch(
        f"/casas/{casa.id}/prestamos/{creado['id']}/confirmacion",
        json={"confirma": False},
        headers=_bearer_de_miembro(client._session_factory, maca_id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["estado_confirmacion"] == "rechazado"

    # Permanente: reintentar confirmar (por cualquiera de las dos partes)
    # responde 400.
    resp2 = client.patch(
        f"/casas/{casa.id}/prestamos/{creado['id']}/confirmacion",
        json={"confirma": True},
        headers=_bearer_de_miembro(client._session_factory, maca_id),
    )
    assert resp2.status_code == 400


def test_tc007_no_se_puede_cambiar_estado_antes_de_confirmar_responde_400(client):
    casa, usuario_id, admin_id, maca_id, _bruno_id = _crear_casa_con_tres_miembros(
        client._session_factory
    )
    creado = _crear_prestamo(client, casa.id, usuario_id, admin_id, maca_id)

    resp = client.patch(
        f"/casas/{casa.id}/prestamos/{creado['id']}",
        json={"estado": "pagado"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400
