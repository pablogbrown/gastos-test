"""T3 — API Routes: `/auth/*` y migración completa de `casas`/`gastos`/
`tareas`/`dashboard` de `X-Usuario-Id` a JWT.

Cubre TC-005 (401 sin JWT válido), TC-006 (JWT válido resuelve el actor
correctamente, mismo comportamiento de negocio que antes) y TC-009
(usuario no-miembro recibe 403), además de `POST /auth/registro` y
`POST /auth/login` end-to-end (no mockeados vía `emitir_token` directo,
como sí hacen los demás archivos de test de rutas — acá se pasa
realmente por el flujo HTTP completo, igual que el recorrido de
"End-to-End Verification" de `10-verify.md`).
"""
import importlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.auth import auth_router
from src.api.routes.casas import casas_router
from src.api.routes.dashboard import dashboard_router
from src.api.routes.gastos import gastos_router
from src.api.routes.tareas import tareas_router

_MIGRACIONES = (
    "0001_casas_miembros",
    "0002_gastos",
    "0003_tareas",
    "0004_historial_actividad",
    "0005_usuarios",
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
    "auth_service",
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
    app.include_router(auth_router)
    app.include_router(casas_router)
    app.include_router(gastos_router)
    app.include_router(tareas_router)
    app.include_router(dashboard_router)
    return TestClient(app)


def _registrar(client, email, password="hunter2", nombre="Pablo"):
    resp = client.post(
        "/auth/registro", json={"email": email, "password": password, "nombre": nombre}
    )
    return resp


def _login(client, email, password="hunter2"):
    return client.post("/auth/login", json={"email": email, "password": password})


def _bearer_de_login(client, email, password="hunter2"):
    resp = _login(client, email, password)
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_registro_crea_usuario_y_devuelve_201(client):
    resp = _registrar(client, "pablo@example.com")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == "pablo@example.com"
    assert "password" not in body
    assert "password_hash" not in body


def test_registro_con_email_duplicado_devuelve_409(client):
    _registrar(client, "pablo@example.com")
    resp = _registrar(client, "pablo@example.com")
    assert resp.status_code == 409


def test_login_con_credenciales_correctas_devuelve_200_con_jwt(client):
    _registrar(client, "pablo@example.com")

    resp = _login(client, "pablo@example.com")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]


def test_login_con_password_incorrecta_devuelve_401(client):
    _registrar(client, "pablo@example.com")

    resp = _login(client, "pablo@example.com", password="incorrecta")
    assert resp.status_code == 401


def test_login_con_email_inexistente_devuelve_401_mismo_mensaje(client):
    _registrar(client, "pablo@example.com")

    resp_email_inexistente = _login(client, "noexiste@example.com")
    resp_password_incorrecta = _login(client, "pablo@example.com", password="incorrecta")

    assert resp_email_inexistente.status_code == 401
    assert resp_password_incorrecta.status_code == 401
    # TC-004: mismo mensaje en ambos casos — no revela qué emails existen.
    assert resp_email_inexistente.json()["detail"] == resp_password_incorrecta.json()["detail"]


def test_ruta_migrada_sin_jwt_responde_401(client):
    """TC-005: reemplaza el 422 que devolvía un `X-Usuario-Id` ausente."""
    resp = client.post("/casas", json={"nombre": "Casa Brown"})
    assert resp.status_code == 401


def test_ruta_migrada_con_jwt_invalido_responde_401(client):
    resp = client.post(
        "/casas",
        json={"nombre": "Casa Brown"},
        headers={"Authorization": "Bearer no-soy-un-jwt-valido"},
    )
    assert resp.status_code == 401


def test_flujo_completo_registro_login_crear_casa_y_agregar_miembro_por_email(client):
    """Recorrido de `10-verify.md` (End-to-End Verification, pasos 1-4)."""
    # 1. POST /auth/registro con un email nuevo → 201.
    reg1 = _registrar(client, "pablo@example.com")
    assert reg1.status_code == 201

    # 2. POST /auth/login con esas credenciales → 200, JWT recibido.
    headers_pablo = _bearer_de_login(client, "pablo@example.com")

    # 3. POST /casas con el JWT → 201, el Miembro admin queda vinculado
    #    al usuario_id (TC-006: el actor se resuelve correctamente desde
    #    el token, mismo comportamiento de negocio que antes).
    casa_resp = client.post("/casas", json={"nombre": "Casa Brown"}, headers=headers_pablo)
    assert casa_resp.status_code == 201, casa_resp.text
    casa = casa_resp.json()
    assert len(casa["miembros"]) == 1
    assert casa["miembros"][0]["rol"] == "admin"

    # 4. Repetir 1-3 con un segundo email, agregar el primer Usuario como
    #    miembro de la segunda casa por su email → el mismo usuario_id
    #    ahora tiene 2 Miembros (TC-007/TC-008).
    _registrar(client, "ana@example.com")
    headers_ana = _bearer_de_login(client, "ana@example.com")
    casa_2_resp = client.post("/casas", json={"nombre": "Casa Verde"}, headers=headers_ana)
    assert casa_2_resp.status_code == 201
    casa_2 = casa_2_resp.json()

    agregar_resp = client.post(
        f"/casas/{casa_2['id']}/miembros",
        json={"nombre": "Pablo", "identificacion": "PABLO1", "email": "pablo@example.com"},
        headers=headers_ana,
    )
    assert agregar_resp.status_code == 201, agregar_resp.text

    # 5. Intentar GET /casas/{id-de-la-segunda-casa}/... con el JWT del
    #    primer login antes de agregarlo como miembro → 403; después de
    #    agregarlo → 200. Ya fue agregado arriba, así que verificamos el
    #    caso "ya es miembro" (200) y el caso "todavía no es miembro" con
    #    una tercera casa nueva de Ana.
    casa_3_resp = client.post("/casas", json={"nombre": "Casa Ajena"}, headers=headers_ana)
    casa_3 = casa_3_resp.json()

    resp_antes = client.get(f"/casas/{casa_3['id']}/miembros", headers=headers_pablo)
    assert resp_antes.status_code == 403

    resp_despues = client.get(f"/casas/{casa_2['id']}/miembros", headers=headers_pablo)
    assert resp_despues.status_code == 200
    assert len(resp_despues.json()) == 2

    # GET /casas/mias: Pablo tiene Miembro activo en Casa Brown y Casa
    # Verde, pero no en Casa Ajena (REQ-006/TC-010).
    mias_resp = client.get("/casas/mias", headers=headers_pablo)
    assert mias_resp.status_code == 200
    nombres_mias = {c["nombre"] for c in mias_resp.json()}
    assert nombres_mias == {"Casa Brown", "Casa Verde"}


def test_usuario_no_miembro_de_casa_ajena_recibe_403_en_ruta_migrada(client):
    """TC-009."""
    _registrar(client, "pablo@example.com")
    headers_pablo = _bearer_de_login(client, "pablo@example.com")
    casa = client.post("/casas", json={"nombre": "Casa Brown"}, headers=headers_pablo).json()

    _registrar(client, "ana@example.com")
    headers_ana = _bearer_de_login(client, "ana@example.com")

    resp = client.get(f"/casas/{casa['id']}/gastos", headers=headers_ana)
    assert resp.status_code == 403
