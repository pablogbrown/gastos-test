"""T3 — API Routes: contrato HTTP de gastos, categorías y balance.

Cubre TC-010 (historial incluye miembros desactivados), los contratos del
"Gate Criteria" de 10-verify.md (400 sin categoría, 403 sin rol admin al
crear categorías), y la migración a JWT de `usuarios-auth` (reemplaza
`X-Usuario-Id`).
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
from src.api.routes.gastos import gastos_router
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
    migration_casas = importlib.import_module("src.db.migrations.0001_casas_miembros")
    migration_gastos = importlib.import_module("src.db.migrations.0002_gastos")
    # 0004 (spec `dashboard-actividad`): `registrar_gasto` dispara un hook
    # a `actividad_service.registrar_actividad`, que requiere la tabla
    # `historial_actividad`.
    migration_actividad = importlib.import_module("src.db.migrations.0004_historial_actividad")
    # 0005 (spec `usuarios-auth`): `agregar_miembro` ahora exige un
    # Usuario real (por email) para vincular al nuevo Miembro.
    migration_usuarios = importlib.import_module("src.db.migrations.0005_usuarios")
    migration_casas.upgrade(engine)
    migration_gastos.upgrade(engine)
    migration_actividad.upgrade(engine)
    migration_usuarios.upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    monkeypatch.setattr("src.services.casa_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.miembro_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.categoria_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.gasto_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.balance_service.get_session", lambda: TestSession())
    monkeypatch.setattr("src.services.actividad_service.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(gastos_router)
    client = TestClient(app)
    client._session_factory = TestSession
    return client


def _crear_casa(client, nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    resp = client.post("/casas", json={"nombre": nombre}, headers=_bearer(usuario_id))
    assert resp.status_code == 201, resp.text
    body = resp.json()
    admin_id = body["miembros"][0]["id"]
    return body, usuario_id, admin_id


def _crear_categoria(client, casa_id, usuario_id, nombre="Supermercado"):
    resp = client.post(
        f"/casas/{casa_id}/categorias",
        json={"nombre": nombre},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_registrar_gasto_sin_categoria_devuelve_400(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={"descripcion": "Compra", "importe": "100.00", "fecha": "2026-01-01"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_registrar_gasto_con_categoria_inexistente_devuelve_400(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra",
            "importe": "100.00",
            "fecha": "2026-01-01",
            "categoria_id": str(uuid.uuid4()),
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_gasto_sin_jwt_devuelve_401(client):
    casa, _usuario_id, _admin_id = _crear_casa(client)
    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={"descripcion": "Compra", "importe": "100.00", "fecha": "2026-01-01"},
    )
    assert resp.status_code == 401


def test_miembro_sin_permisos_recibe_403_al_crear_categoria(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")
    client.post(
        f"/casas/{casa['id']}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    )

    resp = client.post(
        f"/casas/{casa['id']}/categorias",
        json={"nombre": "Ocio"},
        headers=_bearer(ana_usuario.id),
    )
    assert resp.status_code == 403


def test_usuario_no_miembro_de_la_casa_recibe_403(client):
    """TC-009 (`usuarios-auth`)."""
    casa, _usuario_id, _admin_id = _crear_casa(client)
    usuario_ajeno = uuid.uuid4()

    resp = client.get(f"/casas/{casa['id']}/gastos", headers=_bearer(usuario_ajeno))
    assert resp.status_code == 403


def test_registrar_gasto_y_consultar_balance_end_to_end(client):
    casa, usuario_id, admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Compra semanal",
            "importe": "100.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text
    gasto = resp.json()
    assert gasto["pagado_por"] == admin_id
    assert len(gasto["participantes"]) == 1

    balance_resp = client.get(f"/casas/{casa['id']}/balance", headers=_bearer(usuario_id))
    assert balance_resp.status_code == 200
    balance = balance_resp.json()
    assert balance["balances"][0]["miembro_id"] == admin_id


def test_historial_incluye_gastos_de_miembros_desactivados(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)
    ana_usuario = _crear_usuario_de_prueba(client._session_factory, "ana@example.com")
    ana = client.post(
        f"/casas/{casa['id']}/miembros",
        json={"nombre": "Ana", "identificacion": "ANA1", "email": ana_usuario.email},
        headers=_bearer(usuario_id),
    ).json()

    resp = client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Gasto de Ana",
            "importe": "50.00",
            "fecha": "2026-01-01",
            "categoria_id": categoria["id"],
            "pagado_por": ana["id"],
        },
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 201, resp.text

    client.patch(
        f"/casas/{casa['id']}/miembros/{ana['id']}",
        json={"activo": False},
        headers=_bearer(usuario_id),
    )

    historial = client.get(f"/casas/{casa['id']}/gastos", headers=_bearer(usuario_id))
    assert historial.status_code == 200
    descripciones = [g["descripcion"] for g in historial.json()]
    assert "Gasto de Ana" in descripciones


def test_balance_con_mes_de_formato_invalido_devuelve_400(client):
    """TC-003 (spec `balance-mensual`) a nivel HTTP — re-verifica lo que
    `tests/integration/services/balance_mensual.test.py` (T1) prueba a
    nivel de excepción de servicio."""
    casa, usuario_id, _admin_id = _crear_casa(client)

    resp = client.get(
        f"/casas/{casa['id']}/balance?mes=fecha-invalida",
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 400


def test_balance_con_mes_explicito_filtra_los_gastos(client):
    """Spec `balance-mensual`: el query param `mes` se propaga a
    `calcular_balance` — un gasto de agosto no aparece al consultar
    septiembre."""
    casa, usuario_id, admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    client.post(
        f"/casas/{casa['id']}/gastos",
        json={
            "descripcion": "Gasto de agosto",
            "importe": "100.00",
            "fecha": "2026-08-15",
            "categoria_id": categoria["id"],
        },
        headers=_bearer(usuario_id),
    )

    balance_agosto = client.get(
        f"/casas/{casa['id']}/balance?mes=2026-08", headers=_bearer(usuario_id)
    ).json()
    por_id_agosto = {b["miembro_id"]: b for b in balance_agosto["balances"]}
    assert por_id_agosto[admin_id]["pago"] == 100.0

    balance_septiembre = client.get(
        f"/casas/{casa['id']}/balance?mes=2026-09", headers=_bearer(usuario_id)
    ).json()
    por_id_septiembre = {b["miembro_id"]: b for b in balance_septiembre["balances"]}
    assert por_id_septiembre[admin_id]["pago"] == 0


def test_historial_ordenado_por_fecha_descendente(client):
    casa, usuario_id, _admin_id = _crear_casa(client)
    categoria = _crear_categoria(client, casa["id"], usuario_id)

    for descripcion, fecha in [("Primero", "2026-01-01"), ("Segundo", "2026-01-05")]:
        client.post(
            f"/casas/{casa['id']}/gastos",
            json={
                "descripcion": descripcion,
                "importe": "10.00",
                "fecha": fecha,
                "categoria_id": categoria["id"],
            },
            headers=_bearer(usuario_id),
        )

    historial = client.get(f"/casas/{casa['id']}/gastos", headers=_bearer(usuario_id))
    descripciones = [g["descripcion"] for g in historial.json()]
    assert descripciones == ["Segundo", "Primero"]
