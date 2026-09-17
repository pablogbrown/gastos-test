"""T2 (spec `resumen-tarjeta-pago`) — tracking de `ResumenTarjeta`,
rechazo de importación duplicada, threading de `resumen_id`, y
`pagar_resumen`/`listar_resumenes`.

Cubre TC-001 a TC-006 a nivel de servicio (sin HTTP). Reutiliza el mismo
layout de PDF sintético que `tests/integration/services/resumen_importer.
test.py` (columnas fijas, `reportlab`) — self-contained acá también,
mismo criterio de "cada test file arma su propia fixture" que el resto
del proyecto.
"""
import importlib
import io
import uuid
from datetime import date

import pytest
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models.gasto import Gasto
from src.db.models.resumen_tarjeta import ResumenTarjeta
from src.services.casa_service import crear_casa
from src.services.exceptions import ConflictError, NotFoundError
from src.services.miembro_service import agregar_miembro
from src.services.resumen_importer_service import (
    importar_resumen,
    listar_resumenes,
    pagar_resumen,
)
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


def _construir_pdf_resumen_bbva(cierre="27-Ago-26", vencimiento="07-Sep-26"):
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


@pytest.fixture()
def db_session(monkeypatch):
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

    yield TestSession


def _armar_casa_con_tarjeta(db_session):
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
    return casa, admin_id, tarjeta


def _gastos_de(db_session, casa_id):
    session = db_session()
    try:
        return (
            session.query(Gasto)
            .filter(Gasto.casa_id == casa_id)
            .order_by(Gasto.fecha)
            .all()
        )
    finally:
        session.close()


def _resumenes_de(db_session, casa_id):
    session = db_session()
    try:
        return (
            session.query(ResumenTarjeta)
            .filter(ResumenTarjeta.casa_id == casa_id)
            .all()
        )
    finally:
        session.close()


def test_tc001_importar_crea_resumentarjeta_con_datos_correctos_y_pendiente(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)

    resultado = importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)

    resumenes = _resumenes_de(db_session, casa.id)
    assert len(resumenes) == 1
    resumen = resumenes[0]
    assert resumen.id == resultado.resumen_id
    assert resumen.tarjeta_id == tarjeta.id
    assert resumen.casa_id == casa.id
    assert resumen.fecha_cierre.isoformat() == "2026-08-27"
    assert resumen.fecha_vencimiento.isoformat() == "2026-09-07"
    assert str(resumen.saldo_ars) == "125430.50"
    assert str(resumen.saldo_usd) == "340.00"
    assert resumen.estado == "pendiente"
    assert resumen.gastos_creados == resultado.gastos_creados
    assert resumen.gastos_creados > 0


def test_tc002_importar_el_mismo_pdf_dos_veces_rechaza_la_segunda_sin_crear_gastos(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)
    pdf = _construir_pdf_resumen_bbva()

    importar_resumen(casa.id, tarjeta.id, pdf, admin_id)
    gastos_antes = _gastos_de(db_session, casa.id)
    resumenes_antes = _resumenes_de(db_session, casa.id)

    with pytest.raises(ConflictError):
        importar_resumen(casa.id, tarjeta.id, pdf, admin_id)

    gastos_despues = _gastos_de(db_session, casa.id)
    resumenes_despues = _resumenes_de(db_session, casa.id)
    assert len(gastos_despues) == len(gastos_antes)
    assert len(resumenes_despues) == len(resumenes_antes) == 1


def test_tc002b_distinto_cierre_no_se_considera_duplicado(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)
    importar_resumen(
        casa.id,
        tarjeta.id,
        _construir_pdf_resumen_bbva(cierre="27-Ago-26", vencimiento="07-Sep-26"),
        admin_id,
    )

    # Sin lanzar: un cierre distinto es un resumen distinto.
    importar_resumen(
        casa.id,
        tarjeta.id,
        _construir_pdf_resumen_bbva(cierre="27-Sep-26", vencimiento="07-Oct-26"),
        admin_id,
    )

    assert len(_resumenes_de(db_session, casa.id)) == 2


def test_tc003_cada_gasto_creado_directo_cuota_y_suscripcion_queda_vinculado_al_resumen(
    db_session,
):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)

    resultado = importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)

    gastos = _gastos_de(db_session, casa.id)
    # Gasto directo (SUPERMERCADO).
    directo = next(g for g in gastos if "SUPERMERCADO" in g.descripcion)
    assert directo.resumen_id == resultado.resumen_id
    # Cuotas restantes (ELECTRODOMESTICOS).
    cuotas = [g for g in gastos if "ELECTRODOMESTICOS" in g.descripcion]
    assert len(cuotas) == 3
    assert all(g.resumen_id == resultado.resumen_id for g in cuotas)
    # Vía suscripción detectada (NETFLIX).
    netflix = next(g for g in gastos if "NETFLIX" in g.descripcion)
    assert netflix.resumen_id == resultado.resumen_id


def test_tc004_pagar_un_resumen_marca_todos_sus_gastos_y_el_resumen_como_pagados(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)
    resultado = importar_resumen(casa.id, tarjeta.id, _construir_pdf_resumen_bbva(), admin_id)

    resumen_pagado = pagar_resumen(casa.id, resultado.resumen_id, admin_id)

    assert resumen_pagado.estado == "pagado"
    gastos = _gastos_de(db_session, casa.id)
    gastos_del_resumen = [g for g in gastos if g.resumen_id == resultado.resumen_id]
    assert len(gastos_del_resumen) == resultado.gastos_creados
    assert all(g.estado == "pagado" for g in gastos_del_resumen)


def test_tc005_pagar_un_resumen_no_afecta_otros_ni_permite_pagar_dos_veces(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)
    primera = importar_resumen(
        casa.id,
        tarjeta.id,
        _construir_pdf_resumen_bbva(cierre="27-Ago-26", vencimiento="07-Sep-26"),
        admin_id,
    )
    segunda = importar_resumen(
        casa.id,
        tarjeta.id,
        _construir_pdf_resumen_bbva(cierre="27-Sep-26", vencimiento="07-Oct-26"),
        admin_id,
    )

    pagar_resumen(casa.id, primera.resumen_id, admin_id)

    gastos = _gastos_de(db_session, casa.id)
    gastos_segunda = [g for g in gastos if g.resumen_id == segunda.resumen_id]
    assert all(g.estado == "a_pagar" for g in gastos_segunda)

    resumenes = {r.id: r for r in _resumenes_de(db_session, casa.id)}
    assert resumenes[segunda.resumen_id].estado == "pendiente"

    # Pagar el mismo resumen una segunda vez se rechaza.
    with pytest.raises(ConflictError):
        pagar_resumen(casa.id, primera.resumen_id, admin_id)


def test_pagar_resumen_inexistente_responde_notfound(db_session):
    casa, admin_id, _tarjeta = _armar_casa_con_tarjeta(db_session)

    with pytest.raises(NotFoundError):
        pagar_resumen(casa.id, uuid.uuid4(), admin_id)


def test_tc006_listar_resumenes_devuelve_todos_mas_reciente_primero(db_session):
    casa, admin_id, tarjeta = _armar_casa_con_tarjeta(db_session)
    primera = importar_resumen(
        casa.id,
        tarjeta.id,
        _construir_pdf_resumen_bbva(cierre="27-Ago-26", vencimiento="07-Sep-26"),
        admin_id,
    )
    segunda = importar_resumen(
        casa.id,
        tarjeta.id,
        _construir_pdf_resumen_bbva(cierre="27-Sep-26", vencimiento="07-Oct-26"),
        admin_id,
    )

    resumenes = listar_resumenes(casa.id, tarjeta.id)

    assert [r.id for r in resumenes] == [segunda.resumen_id, primera.resumen_id]
    assert [r.estado for r in resumenes] == ["pendiente", "pendiente"]


def test_listar_resumenes_tarjeta_inexistente_responde_notfound(db_session):
    casa, _admin_id, _tarjeta = _armar_casa_con_tarjeta(db_session)

    with pytest.raises(NotFoundError):
        listar_resumenes(casa.id, uuid.uuid4())
