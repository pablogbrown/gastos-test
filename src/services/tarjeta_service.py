"""Servicio de TarjetaCredito: alta, listado, edición, baja (soft-delete)
y cálculo de las tarjetas con alerta de vencimiento cercano (spec
`tarjetas-credito`).

Cubre REQ-001 (crear, campos obligatorios salvo saldo — TC-001/TC-002),
REQ-002 (editar cierre/vencimiento/saldo — TC-003), REQ-003 (eliminar es
soft-delete — TC-004), REQ-004/REQ-005 (`obtener_tarjetas_con_alerta`,
umbral de `UMBRAL_ALERTA_DIAS` días — TC-005/TC-006/TC-007).

`obtener_tarjetas_con_alerta` vive acá (no en `dashboard_service`)
siguiendo el mismo criterio que `generar_gastos_pendientes` vive en
`suscripcion_service`: la lógica de negocio de "qué es una alerta"
pertenece al dominio de la tarjeta, el dashboard solo la consume (Design
Rationale de T2).

No hay guard de rol (a diferencia de `suscripcion_service`, que requiere
Administrador): REQ-001 dice "un miembro puede registrar una tarjeta" —
cualquier miembro activo de la casa, mismo criterio que `gasto_service`/
`tarea_service` vía `requiere_membresia_activa`.
"""
import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.tarjeta_credito import TarjetaCredito
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import requiere_membresia_activa

UMBRAL_ALERTA_DIAS = 7


@dataclass
class TarjetaAlerta:
    """Una tarjeta activa cuyo vencimiento está a `UMBRAL_ALERTA_DIAS`
    días o menos (o ya venció) — lo que `dashboard_service` consume para
    armar el banner de Inicio (REQ-004/REQ-005)."""

    id: UUID
    nombre: str
    banco: str
    fecha_vencimiento_actual: date
    dias_para_vencimiento: int
    vencida: bool


def crear_tarjeta(
    casa_id: UUID,
    miembro_id: UUID,
    banco: str,
    nombre: str,
    ultimos_digitos: str,
    fecha_cierre_actual: date,
    fecha_vencimiento_actual: date,
    actor: UUID,
) -> TarjetaCredito:
    """Registra una tarjeta nueva (REQ-001). Todos los campos son
    obligatorios salvo el saldo, que todavía no se tiene al momento del
    alta (TC-001) — un campo faltante se rechaza con `ValidationError`
    (TC-002)."""
    if not banco or not str(banco).strip():
        raise ValidationError("El banco de la tarjeta no puede estar vacío.")
    if not nombre or not str(nombre).strip():
        raise ValidationError("El nombre de la tarjeta no puede estar vacío.")
    if not ultimos_digitos or not str(ultimos_digitos).strip():
        raise ValidationError("Los últimos 4 dígitos de la tarjeta son obligatorios.")
    if fecha_cierre_actual is None:
        raise ValidationError("La fecha de cierre actual es obligatoria.")
    if fecha_vencimiento_actual is None:
        raise ValidationError("La fecha de vencimiento actual es obligatoria.")

    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        tarjeta = TarjetaCredito(
            id=uuid.uuid4(),
            casa_id=casa_id,
            miembro_id=miembro_id,
            banco=banco.strip(),
            nombre=nombre.strip(),
            ultimos_digitos=str(ultimos_digitos).strip(),
            fecha_cierre_actual=fecha_cierre_actual,
            fecha_vencimiento_actual=fecha_vencimiento_actual,
            activa=True,
        )
        session.add(tarjeta)
        session.commit()
        session.refresh(tarjeta)
        return tarjeta
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def listar_tarjetas(casa_id: UUID) -> List[TarjetaCredito]:
    """Tarjetas activas de la casa (soft-delete: una eliminada no aparece
    en este listado, TC-004)."""
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return (
            session.query(TarjetaCredito)
            .filter(TarjetaCredito.casa_id == casa_id, TarjetaCredito.activa.is_(True))
            .order_by(TarjetaCredito.creado_en)
            .all()
        )
    finally:
        session.close()


def _obtener_tarjeta_activa_o_none(session, casa_id: UUID, tarjeta_id: UUID):
    return (
        session.query(TarjetaCredito)
        .filter(
            TarjetaCredito.casa_id == casa_id,
            TarjetaCredito.id == tarjeta_id,
            TarjetaCredito.activa.is_(True),
        )
        .one_or_none()
    )


def actualizar_tarjeta(
    casa_id: UUID,
    tarjeta_id: UUID,
    actor: UUID,
    fecha_cierre_actual: Optional[date] = None,
    fecha_vencimiento_actual: Optional[date] = None,
    saldo_actual_ars: Optional[Decimal] = None,
    saldo_actual_usd: Optional[Decimal] = None,
) -> TarjetaCredito:
    """Actualiza solo los campos provistos (REQ-002, TC-003) — pensado
    para reflejar manualmente el resumen más reciente; no valida que la
    nueva fecha sea posterior a la anterior."""
    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        tarjeta = _obtener_tarjeta_activa_o_none(session, casa_id, tarjeta_id)
        if tarjeta is None:
            raise NotFoundError(f"La tarjeta {tarjeta_id} no existe en la casa {casa_id}.")

        if fecha_cierre_actual is not None:
            tarjeta.fecha_cierre_actual = fecha_cierre_actual
        if fecha_vencimiento_actual is not None:
            tarjeta.fecha_vencimiento_actual = fecha_vencimiento_actual
        if saldo_actual_ars is not None:
            tarjeta.saldo_actual_ars = saldo_actual_ars
        if saldo_actual_usd is not None:
            tarjeta.saldo_actual_usd = saldo_actual_usd

        session.commit()
        session.refresh(tarjeta)
        return tarjeta
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def eliminar_tarjeta(casa_id: UUID, tarjeta_id: UUID, actor: UUID) -> None:
    """Desactiva (`activa = False`) la tarjeta — soft-delete, preserva el
    registro (REQ-003, TC-004)."""
    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        tarjeta = _obtener_tarjeta_activa_o_none(session, casa_id, tarjeta_id)
        if tarjeta is None:
            raise NotFoundError(f"La tarjeta {tarjeta_id} no existe en la casa {casa_id}.")

        tarjeta.activa = False
        session.commit()
    except (PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def obtener_tarjetas_con_alerta(casa_id: UUID) -> List[TarjetaAlerta]:
    """Tarjetas activas de `casa_id` cuyo vencimiento está a
    `UMBRAL_ALERTA_DIAS` días o menos, incluidas las ya vencidas
    (REQ-004/REQ-005). No valida que `casa_id` exista: si no existe,
    simplemente no hay ninguna tarjeta que iterar (no-op), mismo criterio
    que `generar_gastos_pendientes` — la validación de "casa existe" es
    responsabilidad de quien arma el resto del dashboard.

    `dias_para_vencimiento = (fecha_vencimiento_actual - hoy).days`;
    `vencida = dias_para_vencimiento < 0` (el día mismo del vencimiento
    no cuenta como "ya vencida" — TC-006)."""
    hoy = date.today()

    session = get_session()
    try:
        tarjetas = (
            session.query(TarjetaCredito)
            .filter(TarjetaCredito.casa_id == casa_id, TarjetaCredito.activa.is_(True))
            .all()
        )

        alertas: List[TarjetaAlerta] = []
        for tarjeta in tarjetas:
            dias_para_vencimiento = (tarjeta.fecha_vencimiento_actual - hoy).days
            if dias_para_vencimiento <= UMBRAL_ALERTA_DIAS:
                alertas.append(
                    TarjetaAlerta(
                        id=tarjeta.id,
                        nombre=tarjeta.nombre,
                        banco=tarjeta.banco,
                        fecha_vencimiento_actual=tarjeta.fecha_vencimiento_actual,
                        dias_para_vencimiento=dias_para_vencimiento,
                        vencida=dias_para_vencimiento < 0,
                    )
                )
        return alertas
    finally:
        session.close()
