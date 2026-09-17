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
import uuid
from dataclasses import dataclass
from typing import List
from uuid import UUID

from src.db.base import get_session
from src.db.models.gasto import Gasto
from src.db.models.resumen_tarjeta import ResumenTarjeta
from src.db.models.tarjeta_credito import TarjetaCredito
from src.services import categoria_service, gasto_service, suscripcion_service, tarjeta_service
from src.services.exceptions import ConflictError, NotFoundError
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
    # Spec `resumen-tarjeta-pago`, REQ-001/REQ-003: id del `ResumenTarjeta`
    # persistido en esta importación — el caller (API) lo usa para
    # referenciar el registro recién creado.
    resumen_id: UUID


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
    """Importa un resumen (REQ-001 a REQ-005): parsea el PDF, rechaza un
    duplicado, actualiza la tarjeta con cierre/vencimiento/saldo, y
    enruta cada consumo al mecanismo correcto.

    El PDF se parsea ANTES de tocar la tarjeta (`PdfFormatoNoReconocidoError`
    se propaga tal cual — TC-009, la ruta la traduce a 422 — sin haber
    escrito nada todavía); `tarjeta_service.actualizar_tarjeta` valida por
    su cuenta que `tarjeta_id` existe y pertenece a `casa_id` (`NotFoundError`
    si no), evitando una segunda lectura separada solo para esa validación.

    Spec `resumen-tarjeta-pago`, REQ-002: el chequeo de duplicado
    `(tarjeta_id, fecha_cierre)` corre ANTES de `actualizar_tarjeta` — si
    ya existe un `ResumenTarjeta` con esa combinación, se rechaza con
    `ConflictError` sin tocar la tarjeta ni crear ningún gasto (atómico
    respecto de esta importación).
    """
    resumen = parse_resumen_bbva(pdf_bytes)

    session = get_session()
    try:
        existente = (
            session.query(ResumenTarjeta)
            .filter(
                ResumenTarjeta.tarjeta_id == tarjeta_id,
                ResumenTarjeta.fecha_cierre == resumen.fecha_cierre_actual,
            )
            .one_or_none()
        )
        if existente is not None:
            raise ConflictError(
                f"Ya se importó un resumen con cierre {resumen.fecha_cierre_actual} "
                f"para esta tarjeta el {existente.importado_en}."
            )
    finally:
        session.close()

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

    session = get_session()
    try:
        resumen_registro = ResumenTarjeta(
            id=uuid.uuid4(),
            casa_id=casa_id,
            tarjeta_id=tarjeta_id,
            fecha_cierre=resumen.fecha_cierre_actual,
            fecha_vencimiento=resumen.fecha_vencimiento_actual,
            saldo_ars=resumen.saldo_actual_ars,
            saldo_usd=resumen.saldo_actual_usd,
            gastos_creados=0,
            estado="pendiente",
        )
        session.add(resumen_registro)
        session.commit()
        session.refresh(resumen_registro)
        resumen_id = resumen_registro.id
    finally:
        session.close()

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
                resumen_id=resumen_id,
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
                    # Spec `gastos-estado-pago`, REQ-004: un resumen recien
                    # importado nunca se asume pagado.
                    estado="a_pagar",
                    resumen_id=resumen_id,
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
                # Spec `gastos-estado-pago`, REQ-004: idem el resto de las
                # rutas de creacion de gasto de esta importacion.
                estado="a_pagar",
                resumen_id=resumen_id,
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
                # Spec `gastos-estado-pago`, REQ-004: idem el resto de las
                # rutas de creacion de gasto de esta importacion.
                estado="a_pagar",
                resumen_id=resumen_id,
            )
            gastos_creados += 1

    session = get_session()
    try:
        registro = session.get(ResumenTarjeta, resumen_id)
        registro.gastos_creados = gastos_creados
        session.commit()
    finally:
        session.close()

    return ResumenImportado(
        gastos_creados=gastos_creados,
        cuotas_creadas=cuotas_creadas,
        suscripciones_vinculadas=suscripciones_vinculadas,
        tarjeta=tarjeta,
        resumen_id=resumen_id,
    )


def pagar_resumen(casa_id: UUID, resumen_id: UUID, actor: UUID) -> ResumenTarjeta:
    """Marca un `ResumenTarjeta` y todos sus `Gasto` vinculados como
    `"pagado"`, en una sola operación (spec `resumen-tarjeta-pago`,
    REQ-004): todo-o-nada, sin pago parcial (ver Tradeoffs de spec.md).

    `actor` no se valida contra ningún guard de rol acá — REQ-004 no
    exige Administrador para pagar un resumen (a diferencia de crear una
    Suscripcion), mismo criterio que `actualizar_estado_gasto`
    (`gasto_service.py`, ver [SERV-03]). Se recibe igual, por
    consistencia con el resto de las funciones de este módulo y para no
    cerrar la puerta a un guard futuro sin cambiar la firma.

    Filtra por `resumen_id`, nunca por `tarjeta_id` — un filtro por
    tarjeta pagaría también gastos de otros resúmenes de la misma
    tarjeta (ver Failure Triage de `feat/10-verify.md`, TC-004/TC-005).
    `ConflictError` si el resumen ya está `"pagado"` — no se puede pagar
    dos veces el mismo resumen (TC-005).
    """
    session = get_session()
    try:
        resumen = (
            session.query(ResumenTarjeta)
            .filter(ResumenTarjeta.casa_id == casa_id, ResumenTarjeta.id == resumen_id)
            .one_or_none()
        )
        if resumen is None:
            raise NotFoundError(f"El resumen {resumen_id} no existe en la casa {casa_id}.")
        if resumen.estado == "pagado":
            raise ConflictError(f"El resumen {resumen_id} ya está pagado.")

        session.query(Gasto).filter(Gasto.resumen_id == resumen_id).update(
            {"estado": "pagado"}, synchronize_session=False
        )
        resumen.estado = "pagado"
        session.commit()
        session.refresh(resumen)
        return resumen
    except (NotFoundError, ConflictError):
        session.rollback()
        raise
    finally:
        session.close()


def listar_resumenes(casa_id: UUID, tarjeta_id: UUID) -> List[ResumenTarjeta]:
    """Todos los resúmenes ya importados de una tarjeta, más recientes
    primero (spec `resumen-tarjeta-pago`, REQ-005) — control y
    auditoría."""
    session = get_session()
    try:
        tarjeta = (
            session.query(TarjetaCredito)
            .filter(TarjetaCredito.casa_id == casa_id, TarjetaCredito.id == tarjeta_id)
            .one_or_none()
        )
        if tarjeta is None:
            raise NotFoundError(f"La tarjeta {tarjeta_id} no existe en la casa {casa_id}.")

        return (
            session.query(ResumenTarjeta)
            .filter(ResumenTarjeta.casa_id == casa_id, ResumenTarjeta.tarjeta_id == tarjeta_id)
            .order_by(ResumenTarjeta.fecha_cierre.desc())
            .all()
        )
    finally:
        session.close()
