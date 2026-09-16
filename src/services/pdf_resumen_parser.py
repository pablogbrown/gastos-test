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
# Encabezado real (confirmado contra el PDF de muestra real, no solo el
# fixture sintético original): las 5 etiquetas van en una línea de texto
# y sus 5 valores en la línea SIGUIENTE — nunca en la misma línea que su
# etiqueta. `_parsear_encabezado` busca esta línea de etiquetas y toma
# los 2 primeros grupos de fecha y los 2 primeros montos de la línea de
# valores que la sigue, en orden (cierre, vencimiento, saldo ARS, saldo
# USD) — nunca por posición de columna, porque acá ninguna columna tiene
# ancho fijo garantizado.
_ENCABEZADO_RE = re.compile(
    r"CIERRE ACTUAL\s+VENCIMIENTO ACTUAL\s+SALDO ACTUAL \$\s+SALDO ACTUAL U\$S\s+PAGO M[ÍI]NIMO \$"
)
_CUOTA_RE = re.compile(r"C\.(\d{2})/(\d{2})")
_MONTO_RE = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2}")
_CUPON_RE = re.compile(r"(?<!\d)\d{3,6}(?!\d)")
_TOTAL_CONSUMOS_RE = re.compile(r"^TOTAL CONSUMOS\b")
_IMPUESTOS_RE = re.compile(r"^Impuestos, cargos e intereses\b")
# La tabla de "Consumos" real trae el nombre del titular a continuación
# ("Consumos Pablo Gabriel Brown"), nunca la palabra sola — \b tolera
# ambos casos (con o sin sufijo).
_CONSUMOS_INICIO_RE = re.compile(r"^Consumos\b")
# Distancia máxima (caracteres) a un offset de columna (ars_offset/
# usd_offset) para aceptar un monto como valor real de esa columna, no
# texto libre embebido en la descripción — confirmado contra el PDF real:
# un monto embebido en la descripción (ej. "... USD 2,99 ...") cae a más
# de 10 caracteres de ambos offsets; un valor de columna real siempre cae
# a 4 caracteres o menos del offset correspondiente.
_UMBRAL_COLUMNA = 10


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
    """Concatena el texto de TODAS las páginas del PDF — el resumen real
    trae el encabezado (cierre/vencimiento/saldo) en la página 1 y la
    tabla "Consumos" recién en la página 2 (nunca ambos en la primera
    página, a diferencia de lo que asumía la versión original de este
    parser, que solo leía `pdf.pages[0]`)."""
    import io

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            return "\n".join(pagina.extract_text(layout=True) or "" for pagina in pdf.pages)
    except Exception as exc:  # pragma: no cover - PDF corrupto/no abrible
        raise PdfFormatoNoReconocidoError(
            "El archivo no pudo leerse como un PDF válido."
        ) from exc


def _parsear_encabezado(lineas: List[str]) -> Optional[tuple]:
    """Devuelve `(fecha_cierre, fecha_vencimiento, saldo_ars, saldo_usd)`
    a partir de la fila de valores que sigue a la línea de etiquetas
    "CIERRE ACTUAL VENCIMIENTO ACTUAL SALDO ACTUAL $ SALDO ACTUAL U$S
    PAGO MÍNIMO $" — en el PDF real, la fila de etiquetas y la fila de
    valores son dos líneas de texto consecutivas y distintas, nunca la
    misma línea. `None` si no se encuentra la línea de etiquetas, o si la
    línea que la sigue no trae al menos 2 fechas."""
    for i, linea in enumerate(lineas):
        if _ENCABEZADO_RE.search(linea):
            for valores in lineas[i + 1 :]:
                if not valores.strip():
                    continue
                fechas = [m.group() for m in _FECHA_RE.finditer(valores)]
                montos = [m.group() for m in _MONTO_RE.finditer(valores)]
                if len(fechas) < 2:
                    return None
                return (
                    _parsear_fecha(fechas[0]),
                    _parsear_fecha(fechas[1]),
                    _parsear_monto(montos[0]) if len(montos) >= 1 else None,
                    _parsear_monto(montos[1]) if len(montos) >= 2 else None,
                )
            return None
    return None


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
            continue
        distancia_ars = abs(monto_match.start() - ars_offset)
        distancia_usd = abs(monto_match.start() - usd_offset)
        if min(distancia_ars, distancia_usd) > _UMBRAL_COLUMNA:
            # Confirmado contra el PDF real: una descripción de consumo en
            # dólares suele repetir el monto como texto libre (ej. "GOOGLE
            # *Google O P1ngEt7f USD 2,99"), lejos de ambas columnas reales
            # — se ignora, o quedaría poblando importe_ars Y importe_usd a
            # la vez, violando la exclusión mutua documentada arriba.
            continue
        if distancia_ars <= distancia_usd:
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
    lineas = texto.splitlines()

    try:
        encabezado = _parsear_encabezado(lineas)
    except InvalidOperation as exc:  # pragma: no cover - defensivo
        raise PdfFormatoNoReconocidoError(
            "El PDF no tiene el formato de resumen BBVA Visa Platinum reconocido "
            "(saldo con formato inesperado)."
        ) from exc

    if encabezado is None:
        raise PdfFormatoNoReconocidoError(
            "El PDF no tiene el formato de resumen BBVA Visa Platinum reconocido "
            "(faltan los marcadores de cierre/vencimiento actual)."
        )

    fecha_cierre_actual, fecha_vencimiento_actual, saldo_actual_ars, saldo_actual_usd = encabezado

    consumos: List[ConsumoParseado] = []

    indices_consumos = [i for i, linea in enumerate(lineas) if _CONSUMOS_INICIO_RE.match(linea.strip())]
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
