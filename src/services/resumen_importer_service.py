"""Orquestador de la importación de un resumen de tarjeta en PDF — spec
`importar-resumen-tarjeta`, T2.

Único módulo que toca la base de datos de esta spec: por cada consumo
parseado (`pdf_resumen_parser.parse_resumen_bbva`) decide a qué mecanismo
enrutarlo (gasto normal / cuotas restantes / suscripción detectada) y
llama a los servicios ya existentes — nunca reimplementa su lógica (ver
`00-overview.md`, Arquitectura). La importación es todo-o-nada solo
respecto del PDF en sí (REQ-006, un formato no reconocido no crea ningún
gasto); una vez que el PDF se parseó correctamente, cada línea se procesa
independientemente y una falla de permiso puntual (REQ-004, comercio
nuevo + actor no Administrador) degrada esa línea a gasto suelto en vez
de abortar el resto de la importación.
"""
from dataclasses import dataclass
from uuid import UUID

from src.db.models.tarjeta_credito import TarjetaCredito
from src.services import categoria_service, gasto_service, suscripcion_service, tarjeta_service
from src.services.pdf_resumen_parser import ConsumoParseado, parse_resumen_bbva

# Comercios reconocidos como suscripción — substring case-insensitive
# sobre la descripción del consumo (REQ-004).
SUSCRIPCIONES_RECONOCIDAS = ["NETFLIX", "SPOTIFY", "DISNEY"]

CATEGORIA_IMPORTADO = "Importado"


@dataclass
class ResumenImportado:
    """Resultado de una importación — lo que consume T3/T4 (REQ-002 a
    REQ-004). `gastos_creados` es el TOTAL de filas `Gasto` persistidas
    en esta importación (incluye las de `cuotas_creadas` y las vinculadas
    a `suscripciones_vinculadas`, no es una cuarta categoría aparte)."""

    gastos_creados: int
    cuotas_creadas: int
    suscripciones_vinculadas: int
    tarjeta: TarjetaCredito


def _es_suscripcion_reconocida(descripcion: str) -> bool:
    descripcion_normalizada = descripcion.upper()
    return any(marca in descripcion_normalizada for marca in SUSCRIPCIONES_RECONOCIDAS)


def _moneda_y_monto(consumo: ConsumoParseado):
    if consumo.importe_usd is not None:
        return "USD", consumo.importe_usd
    return "ARS", consumo.importe_ars


def importar_resumen(
    casa_id: UUID, tarjeta_id: UUID, pdf_bytes: bytes, actor: UUID
) -> ResumenImportado:
    """Importa un resumen (REQ-001 a REQ-005): parsea el PDF, actualiza
    la tarjeta con cierre/vencimiento/saldo, y enruta cada consumo al
    mecanismo correcto.

    El PDF se parsea ANTES de tocar la tarjeta (`PdfFormatoNoReconocidoError`
    se propaga tal cual — TC-009, la ruta la traduce a 422 — sin haber
    escrito nada todavía); `tarjeta_service.actualizar_tarjeta` valida por
    su cuenta que `tarjeta_id` existe y pertenece a `casa_id` (`NotFoundError`
    si no), evitando una segunda lectura separada solo para esa validación.
    """
    resumen = parse_resumen_bbva(pdf_bytes)

    tarjeta = tarjeta_service.actualizar_tarjeta(
        casa_id,
        tarjeta_id,
        actor,
        fecha_cierre_actual=resumen.fecha_cierre_actual,
        fecha_vencimiento_actual=resumen.fecha_vencimiento_actual,
        saldo_actual_ars=resumen.saldo_actual_ars,
        saldo_actual_usd=resumen.saldo_actual_usd,
    )

    categoria = categoria_service.obtener_o_crear_categoria(casa_id, CATEGORIA_IMPORTADO, actor)

    gastos_creados = 0
    cuotas_creadas = 0
    suscripciones_vinculadas = 0

    for consumo in resumen.consumos:
        moneda, importe = _moneda_y_monto(consumo)

        if _es_suscripcion_reconocida(consumo.descripcion):
            _suscripcion, degradado = suscripcion_service.registrar_suscripcion_detectada(
                casa_id,
                consumo.descripcion,
                importe,
                categoria.id,
                tarjeta.miembro_id,
                actor,
                moneda,
                consumo.fecha,
                tarjeta_id=tarjeta_id,
            )
            if degradado:
                gasto_service.registrar_gasto(
                    casa_id,
                    consumo.descripcion,
                    importe,
                    consumo.fecha,
                    categoria.id,
                    tarjeta.miembro_id,
                    actor,
                    moneda=moneda,
                    tarjeta_id=tarjeta_id,
                )
                gastos_creados += 1
            else:
                gastos_creados += 1
                suscripciones_vinculadas += 1
        elif consumo.cuota_actual is not None:
            nuevos = gasto_service.registrar_gasto_cuotas_restantes(
                casa_id,
                consumo.descripcion,
                importe,
                consumo.fecha,
                consumo.cuota_actual,
                consumo.cuota_total,
                categoria.id,
                tarjeta.miembro_id,
                actor,
                moneda=moneda,
                tarjeta_id=tarjeta_id,
            )
            gastos_creados += len(nuevos)
            cuotas_creadas += len(nuevos)
        else:
            gasto_service.registrar_gasto(
                casa_id,
                consumo.descripcion,
                importe,
                consumo.fecha,
                categoria.id,
                tarjeta.miembro_id,
                actor,
                moneda=moneda,
                tarjeta_id=tarjeta_id,
            )
            gastos_creados += 1

    return ResumenImportado(
        gastos_creados=gastos_creados,
        cuotas_creadas=cuotas_creadas,
        suscripciones_vinculadas=suscripciones_vinculadas,
        tarjeta=tarjeta,
    )
