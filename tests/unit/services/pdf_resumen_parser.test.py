"""T1 (spec `importar-resumen-tarjeta`) — `pdf_resumen_parser`: parser
puro del resumen BBVA Visa Platinum.

Genera un PDF de fixture sintético con `reportlab` en cada test (sin
datos personales reales, ver `01-plan-01-parser-pdf.md`) reproduciendo
el layout del PDF de muestra: encabezado (cierre/vencimiento/saldo) +
tabla "Consumos" con columnas fijas (fecha, descripción, cupón, importe
en pesos, importe en dólares) + sección "Impuestos, cargos e intereses"
que nunca debe leerse como consumo (TC-008).

Cubre el "Done When" de T1: TC-001 (datos de cierre/vencimiento/saldo),
TC-002/TC-003 (pesos/dólares), TC-004 (datos de una línea en cuotas),
TC-008 (exclusión de impuestos/cargos) y TC-009 (PDF no reconocido).
"""
import io
from decimal import Decimal

import pytest
from reportlab.pdfgen import canvas

from src.services.exceptions import PdfFormatoNoReconocidoError
from src.services.pdf_resumen_parser import parse_resumen_bbva

# Posiciones de columna fijas (puntos) usadas por el PDF de muestra real
# — reproducidas acá para que `layout=True` (pdfplumber) preserve el
# espaciado horizontal real entre columnas, tal como documenta el
# docstring de `pdf_resumen_parser.py`.
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


def _construir_pdf_resumen_bbva(
    *,
    cierre="27-Ago-26",
    vencimiento="07-Sep-26",
    saldo_ars="125.430,50",
    saldo_usd="340,00",
    total_ars="41.199,00",
    total_usd="45,00",
    incluir_consumos=True,
) -> bytes:
    """Construye un PDF sintético con el layout del resumen BBVA Visa
    Platinum: encabezado + tabla "Consumos" (una línea en pesos, una en
    dólares, una en cuotas "C.04/06", una de un comercio reconocido
    "NETFLIX.COM") + sección "Impuestos, cargos e intereses" con líneas
    que NUNCA deben aparecer como consumos parseados."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    y = 800
    c.drawString(40, y, "BBVA Visa Platinum")
    y -= 20
    c.drawString(40, y, "CIERRE ACTUAL")
    c.drawString(200, y, cierre)
    y -= 16
    c.drawString(40, y, "VENCIMIENTO ACTUAL")
    c.drawString(200, y, vencimiento)
    y -= 16
    c.drawString(40, y, "SALDO ACTUAL $")
    c.drawString(200, y, saldo_ars)
    y -= 16
    c.drawString(40, y, "SALDO ACTUAL U$S")
    c.drawString(200, y, saldo_usd)
    y -= 30
    c.drawString(40, y, "Consumos")
    y -= 20

    if incluir_consumos:
        _fila(c, y, "01-Ago-26", "SUPERMERCADO DIA", "1234", "15.200,00", "")
        y -= 16
        _fila(c, y, "03-Ago-26", "AMAZON.COM", "5678", "", "45,00")
        y -= 16
        _fila(c, y, "04-Ago-26", "ELECTRODOMESTICOS SA C.04/06", "9012", "22.000,00", "")
        y -= 16
        _fila(c, y, "05-Ago-26", "NETFLIX.COM", "3456", "3.999,00", "")
        y -= 16
        y -= 4

    _fila(c, y, "", "TOTAL CONSUMOS", "", total_ars, total_usd)
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


def test_tc001_extrae_cierre_vencimiento_saldo_del_encabezado():
    resumen = parse_resumen_bbva(_construir_pdf_resumen_bbva())

    assert resumen.fecha_cierre_actual.isoformat() == "2026-08-27"
    assert resumen.fecha_vencimiento_actual.isoformat() == "2026-09-07"
    assert str(resumen.saldo_actual_ars) == "125430.50"
    assert str(resumen.saldo_actual_usd) == "340.00"


def test_tc002_consumo_en_pesos_queda_en_importe_ars():
    resumen = parse_resumen_bbva(_construir_pdf_resumen_bbva())

    supermercado = next(c for c in resumen.consumos if "SUPERMERCADO" in c.descripcion)
    assert supermercado.fecha.isoformat() == "2026-08-01"
    assert supermercado.importe_ars == Decimal("15200.00")
    assert supermercado.importe_usd is None
    assert supermercado.cuota_actual is None


def test_tc003_consumo_en_dolares_queda_en_importe_usd():
    resumen = parse_resumen_bbva(_construir_pdf_resumen_bbva())

    amazon = next(c for c in resumen.consumos if "AMAZON" in c.descripcion)
    assert amazon.importe_usd == Decimal("45.00")
    assert amazon.importe_ars is None


def test_tc004_linea_con_cuota_extrae_cuota_actual_y_total_y_limpia_la_descripcion():
    resumen = parse_resumen_bbva(_construir_pdf_resumen_bbva())

    electro = next(c for c in resumen.consumos if "ELECTRODOMESTICOS" in c.descripcion)
    assert electro.cuota_actual == 4
    assert electro.cuota_total == 6
    assert electro.importe_ars == Decimal("22000.00")
    assert "C.04/06" not in electro.descripcion


def test_comercio_reconocido_netflix_se_parsea_como_consumo_normal():
    """El parser no distingue Netflix de cualquier otro consumo — la
    detección de suscripción es responsabilidad de T2
    (`resumen_importer_service`)."""
    resumen = parse_resumen_bbva(_construir_pdf_resumen_bbva())

    netflix = next(c for c in resumen.consumos if "NETFLIX" in c.descripcion)
    assert netflix.importe_ars == Decimal("3999.00")
    assert netflix.cuota_actual is None


def test_tc008_lineas_de_impuestos_y_cargos_nunca_generan_consumos():
    resumen = parse_resumen_bbva(_construir_pdf_resumen_bbva())

    descripciones = [c.descripcion for c in resumen.consumos]
    assert not any("COMISION" in d for d in descripciones)
    assert not any("SELLOS" in d for d in descripciones)
    assert len(resumen.consumos) == 4


def test_tc009_pdf_sin_marcadores_esperados_lanza_error():
    with pytest.raises(PdfFormatoNoReconocidoError):
        parse_resumen_bbva(_construir_pdf_no_reconocido())


def test_tc009_pdf_ilegible_lanza_error_no_excepcion_generica():
    with pytest.raises(PdfFormatoNoReconocidoError):
        parse_resumen_bbva(b"esto no es un PDF en absoluto")
