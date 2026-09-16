"""Servicio de Prestamo: alta, listado y cambio de estado de un préstamo
entre dos miembros de una casa (spec `prestamos-entre-miembros`).

Cubre REQ-001 (registro), REQ-002 (prestamista != deudor), REQ-003
(cambio de estado en ambos sentidos), REQ-004 (listado ordenado por
fecha descendente) y REQ-006 (moneda/estado válidos).

Nunca importa ni referencia `Gasto`/`GastoParticipante`/
`balance_service` (REQ-005) — un préstamo es una entidad completamente
independiente, mismo criterio que documenta `00-overview.md`. Reutiliza
`gasto_service.MONEDAS_VALIDAS` por import directo (mismo patrón que ya
usa `suscripcion_service.py` para esa misma constante) en vez de
duplicarla.
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.miembro import Miembro
from src.db.models.prestamo import Prestamo
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.gasto_service import MONEDAS_VALIDAS
from src.services.miembro_service import requiere_membresia_activa

# Únicos valores válidos de `estado` para un Prestamo — mismo criterio
# que `ESTADOS_VALIDOS` de `gasto_service.py`, pero con default invertido
# (un préstamo nace "pendiente", un gasto nace "pagado").
ESTADOS_PRESTAMO_VALIDOS = {"pendiente", "pagado"}


def crear_prestamo(
    casa_id: UUID,
    prestamista_id: UUID,
    deudor_id: UUID,
    importe,
    moneda: str,
    fecha: date,
    actor: UUID,
    descripcion: Optional[str] = None,
) -> Prestamo:
    """Registra un préstamo nuevo, siempre en estado "pendiente"
    (REQ-001/REQ-003, TC-001).

    `prestamista_id`/`deudor_id` deben ser distintos (REQ-002, TC-002) y
    ambos deben ser miembros existentes de la casa. `actor` solo necesita
    ser un miembro activo de la casa (`requiere_membresia_activa`, mismo
    guard que `gasto_service`) — no se exige que sea el prestamista ni el
    deudor (ver Tradeoffs de `00-overview.md`): cualquier miembro activo
    puede registrar un préstamo entre otros dos, mismo nivel de apertura
    que `registrar_gasto`.
    """
    if prestamista_id == deudor_id:
        raise ValidationError("El prestamista y el deudor no pueden ser el mismo miembro.")
    if importe is None or Decimal(str(importe)) <= 0:
        raise ValidationError("El importe del préstamo debe ser mayor a cero.")
    if moneda not in MONEDAS_VALIDAS:
        raise ValidationError(f"Moneda inválida: {moneda!r}. Debe ser 'ARS' o 'USD'.")

    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        prestamista = (
            session.query(Miembro)
            .filter(Miembro.casa_id == casa_id, Miembro.id == prestamista_id)
            .one_or_none()
        )
        if prestamista is None:
            raise NotFoundError(f"El miembro {prestamista_id} no existe en la casa {casa_id}.")

        deudor = (
            session.query(Miembro)
            .filter(Miembro.casa_id == casa_id, Miembro.id == deudor_id)
            .one_or_none()
        )
        if deudor is None:
            raise NotFoundError(f"El miembro {deudor_id} no existe en la casa {casa_id}.")

        prestamo = Prestamo(
            id=uuid.uuid4(),
            casa_id=casa_id,
            prestamista_id=prestamista_id,
            deudor_id=deudor_id,
            importe=Decimal(str(importe)).quantize(Decimal("0.01")),
            moneda=moneda,
            descripcion=descripcion.strip() if descripcion else None,
            fecha=fecha,
            estado="pendiente",
        )
        session.add(prestamo)
        session.commit()
        session.refresh(prestamo)
        return prestamo
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def listar_prestamos(casa_id: UUID) -> List[Prestamo]:
    """Préstamos de la casa, ordenados por fecha descendente (REQ-004,
    TC-005)."""
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return (
            session.query(Prestamo)
            .filter(Prestamo.casa_id == casa_id)
            .order_by(Prestamo.fecha.desc())
            .all()
        )
    finally:
        session.close()


def actualizar_estado_prestamo(
    casa_id: UUID, prestamo_id: UUID, estado: str, actor: UUID
) -> Prestamo:
    """Cambia el `estado` de un préstamo ya existente, en cualquier
    sentido (REQ-003, TC-004). Mismo nivel de permiso que
    `crear_prestamo` — cualquier miembro activo de la casa, sin chequeo
    de rol admin."""
    if estado not in ESTADOS_PRESTAMO_VALIDOS:
        raise ValidationError(f"Estado inválido: {estado!r}. Debe ser 'pendiente' o 'pagado'.")

    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        prestamo = (
            session.query(Prestamo)
            .filter(Prestamo.casa_id == casa_id, Prestamo.id == prestamo_id)
            .one_or_none()
        )
        if prestamo is None:
            raise NotFoundError(f"El préstamo {prestamo_id} no existe en la casa {casa_id}.")

        prestamo.estado = estado
        session.commit()
        session.refresh(prestamo)
        return prestamo
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()
