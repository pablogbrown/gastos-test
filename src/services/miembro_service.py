"""Servicio de Miembro: alta, baja y guard de membresía activa.

Cubre REQ-002, REQ-003, REQ-005 y expone `requiere_membresia_activa`,
el guard transversal que las specs `gastos` y `tareas-puntos` importan
directamente para cumplir REQ-005 (nadie opera sin ser miembro activo).
"""
import uuid
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.miembro import Miembro, RolEnum
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError


def _obtener_miembro_o_none(session, casa_id: UUID, miembro_id: UUID):
    return (
        session.query(Miembro)
        .filter(Miembro.casa_id == casa_id, Miembro.id == miembro_id)
        .one_or_none()
    )


def _validar_actor_admin(session, casa_id: UUID, actor: UUID) -> None:
    actor_miembro = _obtener_miembro_o_none(session, casa_id, actor)
    if actor_miembro is None or not actor_miembro.activo:
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")
    if actor_miembro.rol != RolEnum.ADMIN:
        raise PermissionDeniedError("Solo un Administrador puede realizar esta acción.")


def agregar_miembro(casa_id: UUID, nombre: str, identificacion: str, actor: UUID) -> Miembro:
    """Agrega un nuevo Miembro (rol `member`) a la casa `casa_id`.

    Requiere que `actor` sea Administrador activo de esa casa (TC-006).
    Rechaza identificación duplicada dentro de la misma casa (TC-004),
    delegando la garantía última al constraint único de T1.
    """
    if not nombre or not str(nombre).strip():
        raise ValidationError("El nombre del miembro no puede estar vacío.")
    if not identificacion or not str(identificacion).strip():
        raise ValidationError("La identificación del miembro no puede estar vacía.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        _validar_actor_admin(session, casa_id, actor)

        duplicado = (
            session.query(Miembro)
            .filter(Miembro.casa_id == casa_id, Miembro.identificacion == identificacion)
            .one_or_none()
        )
        if duplicado is not None:
            raise ValidationError(
                f"Ya existe un miembro con identificación {identificacion!r} en esta casa."
            )

        miembro = Miembro(
            id=uuid.uuid4(),
            casa_id=casa_id,
            nombre=nombre.strip(),
            identificacion=identificacion.strip(),
            rol=RolEnum.MEMBER,
            activo=True,
        )
        session.add(miembro)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ValidationError(
                f"Ya existe un miembro con identificación {identificacion!r} en esta casa."
            ) from exc
        session.refresh(miembro)
        return miembro
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def desactivar_miembro(casa_id: UUID, miembro_id: UUID, actor: UUID) -> Miembro:
    """Marca `activo=False` en el miembro indicado (REQ-003, TC-005).

    No borra ni toca el historial de gastos/tareas asociado — solo cambia
    el flag `activo`. Requiere que `actor` sea Administrador activo.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        _validar_actor_admin(session, casa_id, actor)

        miembro = _obtener_miembro_o_none(session, casa_id, miembro_id)
        if miembro is None:
            raise NotFoundError(f"El miembro {miembro_id} no existe en la casa {casa_id}.")

        miembro.activo = False
        session.commit()
        session.refresh(miembro)
        return miembro
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def listar_miembros(casa_id: UUID):
    """Lista todos los miembros (activos e inactivos) de una casa.

    No forma parte de las "Interfaces Produced" de T2 (ninguna spec
    hermana la consume), pero se agrega aquí para que la ruta GET de T3
    siga siendo un adaptador delgado en vez de consultar el modelo
    directamente.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return session.query(Miembro).filter(Miembro.casa_id == casa_id).all()
    finally:
        session.close()


def requiere_membresia_activa(casa_id: UUID, usuario_id: UUID) -> bool:
    """Guard transversal (REQ-005): True si `usuario_id` es miembro activo
    de `casa_id`. Reutilizado por las specs `gastos` y `tareas-puntos`
    antes de permitir registrar un gasto o completar una tarea (TC-008).
    """
    session = get_session()
    try:
        miembro = _obtener_miembro_o_none(session, casa_id, usuario_id)
        return miembro is not None and miembro.activo
    finally:
        session.close()
