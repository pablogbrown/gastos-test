"""T3 (spec `tarjetas-credito`) — API Routes: contrato HTTP de tarjetas.

Cubre los "Gate Criteria" de 10-verify.md: TC-001 a TC-004 a nivel HTTP
(spec `tarjetas-credito`) y, más abajo, los endpoints de resúmenes de la
spec `resumen-tarjeta-pago` (T3: `GET .../resumenes`, `PATCH .../
resumenes/{id}/pagar`, 409 en una importación duplicada).
"""
import importlib
import io
import uuid
from datetime import date, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.casas import casas_router
from src.api.routes.tarjetas import tarjetas_router
from src.services.auth_service import emitir_token
from src.services.casa_service import crear_casa


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
        "0002_gastos",
        "0004_historial_actividad",
        "0005_usuarios",
        "0009_suscripciones",
        "0010_gasto_suscripcion_moneda",
        "0011_tarjetas_credito",
        "0012_gasto_tarjeta_id",
        # Spec `resumen-tarjeta-pago`: necesarias para ejercitar
        # `POST .../resumen` end-to-end (importación real) y los
        # endpoints nuevos de resúmenes.
        "0019_resumen_tarjeta",
    ):
        importlib.import_module(f"src.db.migrations.{nombre}").upgrade(engine)

    TestSession = sessionmaker(bind=engine)
    for modulo in (
        "src.services.casa_service",
        "src.services.miembro_service",
        "src.services.categoria_service",
        "src.services.gasto_service",
        "src.services.actividad_service",
        "src.services.suscripcion_service",
        "src.services.tarjeta_service",
        "src.services.resumen_importer_service",
    ):
        monkeypatch.setattr(f"{modulo}.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(tarjetas_router)
    client = TestClient(app)
    client._session_factory = TestSession
    return client


def _construir_pdf_resumen_bbva(cierre="27-Ago-26", vencimiento="07-Sep-26") -> bytes:
    """Mismo layout sintético que `resumen_importer.test.py`/
    `resumen_tarjeta.test.py` — self-contained acá también, mismo
    criterio de "cada test file arma su propia fixture" que el resto del
    proyecto."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.drawString(40, y, "BBVA Visa Platinum")
    y -= 30
    c.drawString(
        40, y, "CIERRE ACTUAL     VENCIMIENTO ACTUAL     SALDO ACTUAL $     "
        "SALDO ACTUAL U$S     PAGO MÍNIMO $"
    )
    y -= 16
    c.drawString(40, y, f"{cierre}     {vencimiento}     125.430,50     340,00     50.000,00")
    y -= 30
    c.drawString(40, y, "Consumos")
    y -= 20
    c.drawString(40, y, "01-Ago-26")
    c.drawString(110, y, "SUPERMERCADO DIA")
    c.drawString(320, y, "1234")
    c.drawString(400, y, "15.200,00")

    c.save()
    return buffer.getvalue()


def _importar_resumen(client, casa_id, tarjeta_id, usuario_id, cierre="27-Ago-26", vencimiento="07-Sep-26"):
    return client.post(
        f"/casas/{casa_id}/tarjetas/{tarjeta_id}/resumen",
        files={"archivo": ("resumen.pdf", _construir_pdf_resumen_bbva(cierre, vencimiento), "application/pdf")},
        headers=_bearer(usuario_id),
    )


def _crear_casa_directo(nombre="Casa Brown"):
    usuario_id = uuid.uuid4()
    casa = crear_casa(nombre, usuario_id)
    admin_id = casa.miembros[0].id
    return casa, usuario_id, admin_id


def _payload_valido():
    hoy = date.today()
    return {
        "banco": "BBVA",
        "nombre": "Visa Platinum",
        "ultimos_digitos": "1234",
        "fecha_cierre_actual": (hoy - timedelta(days=10)).isoformat(),
        "fecha_vencimiento_actual": (hoy + timedelta(days=30)).isoformat(),
    }


def test_tc001_post_crea_tarjeta_y_aparece_en_el_listado(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.post(
        f"/casas/{casa.id}/tarjetas", json=_payload_valido(), headers=_bearer(usuario_id)
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nombre"] == "Visa Platinum"
    assert body["activa"] is True
    assert body["saldo_actual_ars"] is None

    listado = client.get(f"/casas/{casa.id}/tarjetas", headers=_bearer(usuario_id))
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["id"] == body["id"]


def test_tc002_post_sin_banco_responde_400(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    payload = _payload_valido()
    payload["banco"] = ""

    resp = client.post(f"/casas/{casa.id}/tarjetas", json=payload, headers=_bearer(usuario_id))
    assert resp.status_code == 400


def test_tc003_patch_edita_vencimiento_y_persiste(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    creada = client.post(
        f"/casas/{casa.id}/tarjetas", json=_payload_valido(), headers=_bearer(usuario_id)
    )
    tarjeta_id = creada.json()["id"]
    nuevo_vencimiento = (date.today() + timedelta(days=60)).isoformat()

    resp = client.patch(
        f"/casas/{casa.id}/tarjetas/{tarjeta_id}",
        json={"fecha_vencimiento_actual": nuevo_vencimiento},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["fecha_vencimiento_actual"] == nuevo_vencimiento

    listado = client.get(f"/casas/{casa.id}/tarjetas", headers=_bearer(usuario_id))
    assert listado.json()[0]["fecha_vencimiento_actual"] == nuevo_vencimiento


def test_tc004_delete_saca_la_tarjeta_del_listado_activo(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()
    creada = client.post(
        f"/casas/{casa.id}/tarjetas", json=_payload_valido(), headers=_bearer(usuario_id)
    )
    tarjeta_id = creada.json()["id"]

    resp = client.delete(f"/casas/{casa.id}/tarjetas/{tarjeta_id}", headers=_bearer(usuario_id))
    assert resp.status_code == 204

    listado = client.get(f"/casas/{casa.id}/tarjetas", headers=_bearer(usuario_id))
    assert listado.json() == []


def test_patch_tarjeta_inexistente_responde_404(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.patch(
        f"/casas/{casa.id}/tarjetas/{uuid.uuid4()}",
        json={"saldo_actual_ars": "1000.00"},
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 404


def test_delete_tarjeta_inexistente_responde_404(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.delete(f"/casas/{casa.id}/tarjetas/{uuid.uuid4()}", headers=_bearer(usuario_id))
    assert resp.status_code == 404


def test_post_sin_jwt_devuelve_401(client):
    casa, _usuario_id, _admin_id = _crear_casa_directo()
    resp = client.post(f"/casas/{casa.id}/tarjetas", json=_payload_valido())
    assert resp.status_code == 401


def test_usuario_no_miembro_de_la_casa_recibe_403(client):
    casa, _usuario_id, _admin_id = _crear_casa_directo()
    usuario_ajeno = uuid.uuid4()

    resp = client.post(
        f"/casas/{casa.id}/tarjetas", json=_payload_valido(), headers=_bearer(usuario_ajeno)
    )
    assert resp.status_code == 403


# --- Spec `resumen-tarjeta-pago`, T3 --------------------------------------


def _crear_casa_con_tarjeta(client):
    casa, usuario_id, admin_id = _crear_casa_directo()
    creada = client.post(
        f"/casas/{casa.id}/tarjetas", json=_payload_valido(), headers=_bearer(usuario_id)
    )
    tarjeta_id = creada.json()["id"]
    return casa, usuario_id, admin_id, tarjeta_id


def test_post_resumen_duplicado_responde_409_sin_crear_gastos_adicionales(client):
    casa, usuario_id, _admin_id, tarjeta_id = _crear_casa_con_tarjeta(client)

    primera = _importar_resumen(client, casa.id, tarjeta_id, usuario_id)
    assert primera.status_code == 200, primera.text

    segunda = _importar_resumen(client, casa.id, tarjeta_id, usuario_id)
    assert segunda.status_code == 409

    resumenes = client.get(
        f"/casas/{casa.id}/tarjetas/{tarjeta_id}/resumenes", headers=_bearer(usuario_id)
    )
    assert len(resumenes.json()) == 1


def test_get_resumenes_lista_los_importados(client):
    casa, usuario_id, _admin_id, tarjeta_id = _crear_casa_con_tarjeta(client)
    _importar_resumen(client, casa.id, tarjeta_id, usuario_id, cierre="27-Ago-26", vencimiento="07-Sep-26")
    _importar_resumen(client, casa.id, tarjeta_id, usuario_id, cierre="27-Sep-26", vencimiento="07-Oct-26")

    resp = client.get(
        f"/casas/{casa.id}/tarjetas/{tarjeta_id}/resumenes", headers=_bearer(usuario_id)
    )
    assert resp.status_code == 200, resp.text
    cuerpo = resp.json()
    assert len(cuerpo) == 2
    # Más reciente primero (REQ-005/TC-006).
    assert cuerpo[0]["fecha_cierre"] == "2026-09-27"
    assert cuerpo[1]["fecha_cierre"] == "2026-08-27"
    assert all(r["estado"] == "pendiente" for r in cuerpo)


def test_patch_pagar_resumen_marca_todo_pagado_y_409_en_segundo_pago(client):
    casa, usuario_id, _admin_id, tarjeta_id = _crear_casa_con_tarjeta(client)
    importada = _importar_resumen(client, casa.id, tarjeta_id, usuario_id)
    resumen_id = importada.json()["resumen_id"]

    resp = client.patch(
        f"/casas/{casa.id}/tarjetas/{tarjeta_id}/resumenes/{resumen_id}/pagar",
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["estado"] == "pagado"

    segundo_pago = client.patch(
        f"/casas/{casa.id}/tarjetas/{tarjeta_id}/resumenes/{resumen_id}/pagar",
        headers=_bearer(usuario_id),
    )
    assert segundo_pago.status_code == 409


def test_patch_pagar_resumen_inexistente_responde_404(client):
    casa, usuario_id, _admin_id, tarjeta_id = _crear_casa_con_tarjeta(client)

    resp = client.patch(
        f"/casas/{casa.id}/tarjetas/{tarjeta_id}/resumenes/{uuid.uuid4()}/pagar",
        headers=_bearer(usuario_id),
    )
    assert resp.status_code == 404


def test_get_resumenes_tarjeta_inexistente_responde_404(client):
    casa, usuario_id, _admin_id = _crear_casa_directo()

    resp = client.get(
        f"/casas/{casa.id}/tarjetas/{uuid.uuid4()}/resumenes", headers=_bearer(usuario_id)
    )
    assert resp.status_code == 404
