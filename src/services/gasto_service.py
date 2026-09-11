"""Servicio de Gasto: registro y división entre participantes.

Cubre REQ-001 (registro), REQ-003 (participantes por defecto/explícitos),
REQ-004 (división en partes iguales), REQ-007 (los participantes quedan
fijos al momento del registro) y REQ-008 (historial).

Toda operación de registro llama a `requiere_membresia_activa` — el
guard transversal de la spec `casas-miembros` — exactamente como sus
propios servicios lo exponen para las specs dependientes.
"""
import uuid
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable, List, Optional
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.categoria import Categoria
from src.db.models.gasto import Gasto, GastoParticipante
from src.db.models.historial_actividad import TipoActividadEnum
from src.db.models.miembro import Miembro
from src.services.actividad_service import registrar_actividad
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import requiere_membresia_activa


def registrar_gasto(
    casa_id: UUID,
    descripcion: str,
    importe,
    fecha,
    categoria_id: Optional[UUID],
    pagado_por: UUID,
    actor: UUID,
    participantes: Optional[Iterable[UUID]] = None,
) -> Gasto:
    """Registra un Gasto y sus GastoParticipante asociados.

    `participantes=None` (o vacío) aplica el gasto a todos los miembros
    activos de la casa al momento del registro (REQ-003/TC-004); una
    lista explícita restringe la división a esos miembros (TC-005). El
    importe se divide en partes iguales, ajustando el redondeo en el
    último participante (REQ-004/TC-006).
    """
    if not descripcion or not str(descripcion).strip():
        raise ValidationError("La descripción del gasto no puede estar vacía.")
    if importe is None or Decimal(str(importe)) <= 0:
        raise ValidationError("El importe del gasto debe ser mayor a cero.")
    if categoria_id is None:
        raise ValidationError("El gasto debe tener una categoría asignada.")

    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        categoria = (
            session.query(Categoria)
            .filter(Categoria.id == categoria_id, Categoria.casa_id == casa_id)
            .one_or_none()
        )
        if categoria is None:
            raise ValidationError("La categoría indicada no existe en esta casa.")

        pagador = (
            session.query(Miembro)
            .filter(Miembro.casa_id == casa_id, Miembro.id == pagado_por)
            .one_or_none()
        )
        if pagador is None:
            raise NotFoundError(f"El miembro {pagado_por} no existe en la casa {casa_id}.")

        miembros_participantes = _resolver_participantes(session, casa_id, participantes)
        if not miembros_participantes:
            raise ValidationError(
                "No hay miembros activos disponibles para dividir el gasto."
            )

        importe_decimal = Decimal(str(importe)).quantize(Decimal("0.01"))
        partes = _dividir_importe(importe_decimal, len(miembros_participantes))

        gasto = Gasto(
            id=uuid.uuid4(),
            casa_id=casa_id,
            descripcion=descripcion.strip(),
            importe=importe_decimal,
            fecha=fecha,
            pagado_por=pagado_por,
            categoria_id=categoria_id,
        )
        session.add(gasto)
        session.flush()

        for miembro, parte in zip(miembros_participantes, partes):
            session.add(
                GastoParticipante(
                    gasto_id=gasto.id, miembro_id=miembro.id, monto_correspondiente=parte
                )
            )

        session.commit()
        session.refresh(gasto)
        _ = gasto.participantes  # fuerza la carga antes de cerrar la sesión

        # Hook de actividad (REQ-002/TC-003, spec `dashboard-actividad`):
        # se dispara recién después del commit de arriba, nunca antes,
        # para que la entrada de actividad no describa un gasto que en
        # definitiva no llegó a confirmarse.
        registrar_actividad(
            casa_id,
            TipoActividadEnum.GASTO_REGISTRADO,
            pagado_por,
            f"{pagador.nombre} registró un gasto de ${importe_decimal} "
            f"({gasto.descripcion}).",
        )

        return gasto
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def _resolver_participantes(session, casa_id: UUID, participantes: Optional[Iterable[UUID]]):
    if participantes:
        ids_unicos = list(dict.fromkeys(participantes))
        miembros = (
            session.query(Miembro)
            .filter(Miembro.casa_id == casa_id, Miembro.id.in_(ids_unicos))
            .all()
        )
        if len(miembros) != len(ids_unicos):
            raise NotFoundError("Uno o más participantes no pertenecen a esta casa.")
        return miembros

    return (
        session.query(Miembro)
        .filter(Miembro.casa_id == casa_id, Miembro.activo.is_(True))
        .all()
    )


def _dividir_importe(importe: Decimal, cantidad: int) -> List[Decimal]:
    """Divide `importe` en `cantidad` partes iguales, ajustando el
    redondeo en la última parte para que la suma sea exactamente
    `importe` (REQ-004, TC-006)."""
    parte = (importe / cantidad).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    partes = [parte] * (cantidad - 1)
    ultima = importe - sum(partes)
    partes.append(ultima)
    return partes


def listar_gastos(casa_id: UUID):
    """Historial de gastos de una casa, ordenado por fecha descendente
    (REQ-008/TC-010). Incluye gastos pagados por miembros ya
    desactivados: no se filtra por `Miembro.activo`.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        gastos = (
            session.query(Gasto)
            .filter(Gasto.casa_id == casa_id)
            .order_by(Gasto.fecha.desc())
            .all()
        )
        for gasto in gastos:
            _ = gasto.participantes
        return gastos
    finally:
        session.close()
