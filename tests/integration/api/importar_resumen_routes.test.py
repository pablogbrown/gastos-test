"""T3 (spec `importar-resumen-tarjeta`) — API Routes: contrato HTTP de
`POST /casas/{casa_id}/tarjetas/{tarjeta_id}/resumen`.

Cubre los "Done When" de T3: un POST con el PDF de ejemplo responde 200
con los contadores esperados, y TC-009 (PDF no reconocible) responde 422
sin crear ningún gasto.
"""
import importlib
import io
import uuid
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.routes.casas import casas_router
from src.api.routes.tarjetas import tarjetas_router
from src.db.models.gasto import Gasto
from src.services.auth_service import emitir_token
from src.services.casa_service import crear_casa
from src.services.tarjeta_service import crear_tarjeta

_X_FECHA = 40
_X_DESC = 110
_X_CUPON = 320
_X_ARS = 400
_X_USD = 470


def _fila(c, y, fecha="", desc="", cupon="", ars="", usd=""):
    if fecha:
        c.drawString(_X_FECHA, y, fecha)
    if desc:
        c.drawString(_X_DESC, y, desc)
    if cupon:
        c.drawString(_X_CUPON, y, cupon)
    if ars:
        c.drawString(_X_ARS, y, ars)
    if usd:
        c.drawString(_X_USD, y, usd)


def _construir_pdf_resumen_bbva() -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.drawString(40, y, "BBVA Visa Platinum")
    y -= 20
    c.drawString(40, y, "CIERRE ACTUAL")
    c.drawString(200, y, "27-Ago-26")
    y -= 16
    c.drawString(40, y, "VENCIMIENTO ACTUAL")
    c.drawString(200, y, "07-Sep-26")
    y -= 16
    c.drawString(40, y, "SALDO ACTUAL $")
    c.drawString(200, y, "125.430,50")
    y -= 16
    c.drawString(40, y, "SALDO ACTUAL U$S")
    c.drawString(200, y, "340,00")
    y -= 30
    c.drawString(40, y, "Consumos")
    y -= 20

    _fila(c, y, "01-Ago-26", "SUPERMERCADO DIA", "1234", "15.200,00", "")
    y -= 16
    _fila(c, y, "03-Ago-26", "AMAZON.COM", "5678", "", "45,00")
    y -= 16
    _fila(c, y, "04-Ago-26", "ELECTRODOMESTICOS SA C.04/06", "9012", "22.000,00", "")
    y -= 16
    _fila(c, y, "05-Ago-26", "NETFLIX.COM", "3456", "3.999,00", "")
    y -= 16
    y -= 4

    _fila(c, y, "", "TOTAL CONSUMOS", "", "41.199,00", "45,00")
    y -= 20
    c.drawString(40, y, "Impuestos, cargos e intereses")
    y -= 20
    _fila(c, y, "06-Ago-26", "COMISION PLATINUM", "0000", "2.500,00", "")
    y -= 16
    _fila(c, y, "07-Ago-26", "IMPUESTO DE SELLOS", "0000", "850,00", "")

    c.save()
    return buffer.getvalue()


def _construir_pdf_no_reconocido() -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(40, 800, "Este es un documento cualquiera, no un resumen BBVA.")
    c.save()
    return buffer.getvalue()


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
    ):
        monkeypatch.setattr(f"{modulo}.get_session", lambda: TestSession())

    app = FastAPI()
    app.include_router(casas_router)
    app.include_router(tarjetas_router)
    client = TestClient(app)
    client._session_factory = TestSession
    return client


def _crear_casa_con_tarjeta():
    usuario_id = uuid.uuid4()
    casa = crear_casa("Casa Brown", usuario_id)
    admin_id = casa.miembros[0].id
    tarjeta = crear_tarjeta(
        casa.id,
        admin_id,
        "BBVA",
        "Visa Platinum",
        "1234",
        date(2026, 7, 27),
        date(2026, 8, 7),
        admin_id,
    )
    return casa, usuario_id, admin_id, tarjeta


def test_post_resumen_con_pdf_de_ejemplo_responde_200_con_contadores_esperados(client):
    casa, usuario_id, _admin_id, tarjeta = _crear_casa_con_tarjeta()

    resp = client.post(
        f"/casas/{casa.id}/tarjetas/{tarjeta.id}/resumen",
        files={"archivo": ("resumen.pdf", _construir_pdf_resumen_bbva(), "application/pdf")},
        headers=_bearer(usuario_id),
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    # 4 consumos totales: 1 normal ARS + 1 normal USD + 3 cuotas
    # restantes (C.04/06) + 1 suscripción (NETFLIX.COM) = 6 gastos.
    assert body["gastos_creados"] == 6
    assert body["cuotas_creadas"] == 3
    assert body["suscripciones_vinculadas"] == 1
    assert body["tarjeta"]["fecha_vencimiento_actual"] == "2026-09-07"
    assert body["tarjeta"]["saldo_actual_ars"] == 125430.50


def test_tc009_post_resumen_con_pdf_no_reconocido_responde_422_sin_crear_gastos(client):
    casa, usuario_id, _admin_id, tarjeta = _crear_casa_con_tarjeta()

    resp = client.post(
        f"/casas/{casa.id}/tarjetas/{tarjeta.id}/resumen",
        files={"archivo": ("otro.pdf", _construir_pdf_no_reconocido(), "application/pdf")},
        headers=_bearer(usuario_id),
    )

    assert resp.status_code == 422, resp.text

    session = client._session_factory()
    try:
        assert session.query(Gasto).filter(Gasto.casa_id == casa.id).count() == 0
    finally:
        session.close()


def test_post_resumen_con_tarjeta_inexistente_responde_404(client):
    casa, usuario_id, _admin_id, _tarjeta = _crear_casa_con_tarjeta()

    resp = client.post(
        f"/casas/{casa.id}/tarjetas/{uuid.uuid4()}/resumen",
        files={"archivo": ("resumen.pdf", _construir_pdf_resumen_bbva(), "application/pdf")},
        headers=_bearer(usuario_id),
    )

    assert resp.status_code == 404


def test_post_resumen_sin_jwt_devuelve_401(client):
    casa, _usuario_id, _admin_id, tarjeta = _crear_casa_con_tarjeta()

    resp = client.post(
        f"/casas/{casa.id}/tarjetas/{tarjeta.id}/resumen",
        files={"archivo": ("resumen.pdf", _construir_pdf_resumen_bbva(), "application/pdf")},
    )

    assert resp.status_code == 401
