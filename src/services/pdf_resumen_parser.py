"""Parser puro del resumen de tarjeta en PDF (formato BBVA Visa Platinum)
— spec `importar-resumen-tarjeta`, T1.

Sin ninguna dependencia de DB ni de otros servicios: recibe los bytes del
PDF y devuelve un `ResumenParseado`, o lanza `PdfFormatoNoReconocidoError`
si no reconoce el formato — nunca un resultado parcial (REQ-006, TC-009).
Se puede testear con un PDF de fixture sin tocar Postgres, igual que
cualquier función pura del proyecto (ver `00-overview.md`, Design
Rationale).

**Advertencia de alcance**: reconoce específicamente el layout del PDF de
muestra (BBVA Visa Platinum) — un resumen de otro banco, u otro diseño del
mismo banco, no tiene por qué reconocerse.

Estrategia de extracción: `pdfplumber` con `layout=True` preserva el
espaciado horizontal proporcional a la posición real de cada palabra en la
página, así que las columnas de la tabla "Consumos" (fecha, descripción,
cupón, importe en pesos, importe en dólares) quedan separadas por
corridas de espacios múltiples, tal como aparecen en el PDF de muestra.
Para decidir si un importe encontrado en una línea de consumo es la
columna "pesos" o la columna "dólares" (ambas pueden estar vacías salvo
una, y una columna vacía no deja ningún rastro en el texto), se usa la
línea "TOTAL CONSUMOS" como referencia: esa fila siempre trae ambos
totales poblados, así que sus dos posiciones de columna (offset de
carácter en la línea) sirven de ancla para clasificar el importe de cada
línea de consumo por cercanía — sin asumir un ancho de columna fijo en
puntos/caracteres.
"""
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List, Optional

import pdfplumber

from src.services.exceptions import PdfFormatoNoReconocidoError

_MESES = {
    "ene": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
}

_FECHA_RE = re.compile(r"(\d{2})-([A-Za-z]{3})-(\d{2})")
_CIERRE_RE = re.compile(r"CIERRE ACTUAL\s+(\d{2}-[A-Za-z]{3}-\d{2})")
_VENCIMIENTO_RE = re.compile(r"VENCIMIENTO ACTUAL\s+(\d{2}-[A-Za-z]{3}-\d{2})")
_SALDO_ARS_RE = re.compile(r"SALDO ACTUAL \$\s+([\d.,]+)")
_SALDO_USD_RE = re.compile(r"SALDO ACTUAL U\$S\s+([\d.,]+)")
_CUOTA_RE = re.compile(r"C\.(\d{2})/(\d{2})")
_MONTO_RE = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2}")
_CUPON_RE = re.compile(r"(?<!\d)\d{3,6}(?!\d)")
_TOTAL_CONSUMOS_RE = re.compile(r"^TOTAL CONSUMOS\b")
_IMPUESTOS_RE = re.compile(r"^Impuestos, cargos e intereses\b")


@dataclass
class ConsumoParseado:
    """Una línea de la tabla "Consumos" del resumen (REQ-002/REQ-003).

    `cuota_actual`/`cuota_total` son `None` para un consumo sin patrón
    "C.NN/NN"; `importe_ars`/`importe_usd` son mutuamente excluyentes —
    exactamente uno de los dos está poblado, según en qué columna del PDF
    apareció el importe.
    """

    fecha: date
    descripcion: str
    cuota_actual: Optional[int] = None
    cuota_total: Optional[int] = None
    importe_ars: Optional[Decimal] = None
    importe_usd: Optional[Decimal] = None


@dataclass
class ResumenParseado:
    """El resultado completo de parsear un resumen (REQ-001 a REQ-005).

    `saldo_actual_ars`/`saldo_actual_usd` son `None` si esa línea del
    encabezado no aparece en el PDF (no todo resumen tiene consumo en
    ambas monedas) — a diferencia de `fecha_cierre_actual`/`fecha_
    vencimiento_actual`, cuya ausencia es justamente lo que dispara
    `PdfFormatoNoReconocidoError`.
    """

    fecha_cierre_actual: date
    fecha_vencimiento_actual: date
    saldo_actual_ars: Optional[Decimal] = None
    saldo_actual_usd: Optional[Decimal] = None
    consumos: List[ConsumoParseado] = field(default_factory=list)


def _parsear_fecha(texto: str) -> date:
    match = _FECHA_RE.search(texto)
    dia, mes_str, anio_corto = match.groups()
    mes = _MESES[mes_str.lower()]
    anio = 2000 + int(anio_corto)
    return date(anio, mes, int(dia))


def _parsear_monto(texto: str) -> Decimal:
    # Formato AR: "." de miles, "," decimal -> normalizar a Decimal.
    return Decimal(texto.replace(".", "").replace(",", "."))


def _extraer_texto(pdf_bytes: bytes) -> str:
    import io

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if not pdf.pages:
                return ""
            return pdf.pages[0].extract_text(layout=True) or ""
    except Exception as exc:  # pragma: no cover - PDF corrupto/no abrible
        raise PdfFormatoNoReconocidoError(
            "El archivo no pudo leerse como un PDF válido."
        ) from exc


def _extraer_offsets_columnas(lineas: List[str]) -> Optional[tuple]:
    """Devuelve `(offset_ars, offset_usd)` a partir de la línea "TOTAL
    CONSUMOS" (siempre trae ambos totales poblados) — ancla para
    clasificar los importes de cada línea de consumo por cercanía de
    columna. `None` si esa línea no aparece o no trae dos importes."""
    for linea in lineas:
        if _TOTAL_CONSUMOS_RE.match(linea.strip()):
            montos = list(_MONTO_RE.finditer(linea))
            if len(montos) >= 2:
                return montos[0].start(), montos[1].start()
            return None
    return None


def _parsear_consumo(linea: str, offsets_columnas: Optional[tuple]) -> Optional[ConsumoParseado]:
    fecha_match = _FECHA_RE.search(linea)
    if fecha_match is None:
        return None

    fecha = _parsear_fecha(fecha_match.group())
    resto = linea[fecha_match.end():]

    cuota_actual: Optional[int] = None
    cuota_total: Optional[int] = None
    cuota_match = _CUOTA_RE.search(resto)
    if cuota_match:
        cuota_actual, cuota_total = int(cuota_match.group(1)), int(cuota_match.group(2))
        resto = resto[: cuota_match.start()] + resto[cuota_match.end():]

    importe_ars: Optional[Decimal] = None
    importe_usd: Optional[Decimal] = None
    ars_offset, usd_offset = offsets_columnas if offsets_columnas else (None, None)

    for monto_match in _MONTO_RE.finditer(linea):
        if monto_match.start() <= fecha_match.end():
            continue
        valor = _parsear_monto(monto_match.group())
        if ars_offset is None or usd_offset is None:
            # Sin ancla de columnas (no había línea TOTAL CONSUMOS con
            # ambos totales): único importe encontrado -> se asume pesos,
            # el caso más común de un resumen sin consumos en dólares.
            importe_ars = valor
        elif abs(monto_match.start() - ars_offset) <= abs(monto_match.start() - usd_offset):
            importe_ars = valor
        else:
            importe_usd = valor

    descripcion = _MONTO_RE.sub(" ", resto)
    descripcion = _CUPON_RE.sub(" ", descripcion)
    descripcion = re.sub(r"\s+", " ", descripcion).strip()

    return ConsumoParseado(
        fecha=fecha,
        descripcion=descripcion,
        cuota_actual=cuota_actual,
        cuota_total=cuota_total,
        importe_ars=importe_ars,
        importe_usd=importe_usd,
    )


def parse_resumen_bbva(pdf_bytes: bytes) -> ResumenParseado:
    """Parsea un resumen de tarjeta en formato BBVA Visa Platinum
    (REQ-001 a REQ-005).

    Lanza `PdfFormatoNoReconocidoError` (REQ-006, TC-009) si no encuentra
    los marcadores "CIERRE ACTUAL"/"VENCIMIENTO ACTUAL" del encabezado —
    nunca devuelve un resultado parcial. Las líneas de "Impuestos, cargos
    e intereses" nunca se leen como consumos (TC-008): la sección
    "Consumos" termina en la primera línea que matchea "TOTAL CONSUMOS" o
    "Impuestos, cargos e intereses", lo que aparezca primero.
    """
    texto = _extraer_texto(pdf_bytes)

    cierre_match = _CIERRE_RE.search(texto)
    vencimiento_match = _VENCIMIENTO_RE.search(texto)
    if cierre_match is None or vencimiento_match is None:
        raise PdfFormatoNoReconocidoError(
            "El PDF no tiene el formato de resumen BBVA Visa Platinum reconocido "
            "(faltan los marcadores de cierre/vencimiento actual)."
        )

    fecha_cierre_actual = _parsear_fecha(cierre_match.group(1))
    fecha_vencimiento_actual = _parsear_fecha(vencimiento_match.group(1))

    saldo_ars_match = _SALDO_ARS_RE.search(texto)
    saldo_usd_match = _SALDO_USD_RE.search(texto)
    try:
        saldo_actual_ars = (
            _parsear_monto(saldo_ars_match.group(1)) if saldo_ars_match else None
        )
        saldo_actual_usd = (
            _parsear_monto(saldo_usd_match.group(1)) if saldo_usd_match else None
        )
    except InvalidOperation as exc:  # pragma: no cover - defensivo
        raise PdfFormatoNoReconocidoError(
            "El PDF no tiene el formato de resumen BBVA Visa Platinum reconocido "
            "(saldo con formato inesperado)."
        ) from exc

    lineas = texto.splitlines()
    consumos: List[ConsumoParseado] = []

    indices_consumos = [i for i, linea in enumerate(lineas) if linea.strip() == "Consumos"]
    if indices_consumos:
        inicio = indices_consumos[0] + 1
        fin = len(lineas)
        for i in range(inicio, len(lineas)):
            texto_linea = lineas[i].strip()
            if _TOTAL_CONSUMOS_RE.match(texto_linea) or _IMPUESTOS_RE.match(texto_linea):
                fin = i
                break

        offsets_columnas = _extraer_offsets_columnas(lineas)
        for linea in lineas[inicio:fin]:
            if not linea.strip():
                continue
            consumo = _parsear_consumo(linea, offsets_columnas)
            if consumo is not None:
                consumos.append(consumo)

    return ResumenParseado(
        fecha_cierre_actual=fecha_cierre_actual,
        fecha_vencimiento_actual=fecha_vencimiento_actual,
        saldo_actual_ars=saldo_actual_ars,
        saldo_actual_usd=saldo_actual_usd,
        consumos=consumos,
    )
