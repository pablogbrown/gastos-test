"""Servicio de Tarea: alta, finalización y recurrencia (REQ-001 a REQ-004,
REQ-007, REQ-008).

Reutiliza el guard `requiere_membresia_activa` de la spec `casas-miembros`
tal como la usan internamente `casa_service`/`miembro_service` — ninguna
regla de membresía se reimplementa aquí.
"""
import uuid
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.historial_tarea import HistorialTarea
from src.db.models.miembro import Miembro, RolEnum
from src.db.models.tarea import EstadoTareaEnum, Tarea
from src.services.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import requiere_membresia_activa

_DIAS_POR_FRECUENCIA = {"diaria": 1, "semanal": 7, "quincenal": 14}


def _obtener_miembro(session, casa_id: UUID, miembro_id: UUID) -> Optional[Miembro]:
    return (
        session.query(Miembro)
        .filter(Miembro.casa_id == casa_id, Miembro.id == miembro_id)
        .one_or_none()
    )


def crear_tarea(
    casa_id: UUID,
    nombre: str,
    puntos: Optional[int],
    *,
    descripcion: Optional[str] = None,
    responsable_id: Optional[UUID] = None,
    fecha_prevista: Optional[date] = None,
    recurrente: bool = False,
    frecuencia: Optional[str] = None,
    actor: UUID,
) -> Tarea:
    """Crea una Tarea en estado Pendiente (REQ-001, REQ-002, TC-001, TC-003).

    Rechaza nombre vacío o puntos faltantes/negativos (TC-002). Requiere que
    `actor` sea miembro activo de `casa_id` (guard de `casas-miembros`).
    """
    if not nombre or not str(nombre).strip():
        raise ValidationError("El nombre de la tarea no puede estar vacío.")
    if puntos is None or isinstance(puntos, bool) or not isinstance(puntos, int) or puntos < 0:
        raise ValidationError(
            "La cantidad de puntos es obligatoria y debe ser un entero no negativo."
        )
    if recurrente and not frecuencia:
        raise ValidationError("Una tarea recurrente debe indicar una frecuencia.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        if not requiere_membresia_activa(casa_id, actor):
            raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")
        if responsable_id is not None and _obtener_miembro(session, casa_id, responsable_id) is None:
            raise NotFoundError(f"El responsable {responsable_id} no es miembro de esta casa.")

        tarea = Tarea(
            id=uuid.uuid4(),
            casa_id=casa_id,
            nombre=nombre.strip(),
            descripcion=descripcion,
            puntos=puntos,
            responsable_id=responsable_id,
            fecha_prevista=fecha_prevista,
            estado=EstadoTareaEnum.PENDIENTE,
            recurrente=bool(recurrente),
            frecuencia=frecuencia,
        )
        session.add(tarea)
        session.commit()
        session.refresh(tarea)
        return tarea
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def completar_tarea(tarea_id: UUID, miembro_id: UUID, actor: UUID) -> HistorialTarea:
    """Marca una Tarea como Completada y registra el `HistorialTarea`
    correspondiente (REQ-004, TC-005).

    Reglas de autorización (TC-004): si la tarea tiene `responsable_id`,
    solo ese miembro (o un Administrador actuando en su nombre) puede
    completarla; si no tiene responsable, cualquier miembro activo puede
    tomarla, pero siempre debe ser el propio miembro quien recibe el
    crédito (o un Administrador registrándolo en su nombre). Rechaza
    completar una tarea ya Completada sin otorgar puntos adicionales
    (TC-006).
    """
    session = get_session()
    try:
        tarea = session.get(Tarea, tarea_id)
        if tarea is None:
            raise NotFoundError(f"La tarea {tarea_id} no existe.")

        casa_id = tarea.casa_id

        actor_miembro = _obtener_miembro(session, casa_id, actor)
        if actor_miembro is None or not actor_miembro.activo:
            raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

        beneficiario = _obtener_miembro(session, casa_id, miembro_id)
        if beneficiario is None or not beneficiario.activo:
            raise NotFoundError(f"El miembro {miembro_id} no es un miembro activo de esta casa.")

        es_admin = actor_miembro.rol == RolEnum.ADMIN
        if tarea.responsable_id is not None:
            if miembro_id != tarea.responsable_id or (actor != miembro_id and not es_admin):
                raise PermissionDeniedError(
                    "Solo el responsable asignado (o un Administrador) puede completar esta tarea."
                )
        elif actor != miembro_id and not es_admin:
            raise PermissionDeniedError(
                "Solo el propio miembro (o un Administrador) puede registrar su finalización."
            )

        if tarea.estado == EstadoTareaEnum.COMPLETADA:
            raise ConflictError(f"La tarea {tarea_id} ya fue completada.")

        historial = HistorialTarea(
            id=uuid.uuid4(),
            tarea_id=tarea.id,
            miembro_id=miembro_id,
            puntos_obtenidos=tarea.puntos,
        )
        session.add(historial)
        tarea.estado = EstadoTareaEnum.COMPLETADA
        session.commit()
        session.refresh(historial)
        return historial
    except (ValidationError, PermissionDeniedError, NotFoundError, ConflictError):
        session.rollback()
        raise
    finally:
        session.close()


def _siguiente_fecha_prevista(
    fecha_prevista: Optional[date], frecuencia: Optional[str]
) -> Optional[date]:
    if fecha_prevista is None or frecuencia is None:
        return None
    dias = _DIAS_POR_FRECUENCIA.get(frecuencia)
    if dias is None:
        return None
    return fecha_prevista + timedelta(days=dias)


def procesar_recurrencia(tarea_id: UUID) -> Optional[Tarea]:
    """Si la Tarea `tarea_id` (ya completada) es recurrente, crea una nueva
    instancia en estado Pendiente con la misma definición (REQ-007,
    TC-009). Devuelve `None` si la tarea no es recurrente — la instancia
    completada nunca se reabre, para que `HistorialTarea` mantenga una
    relación 1:1 clara con la finalización concreta que la generó.
    """
    session = get_session()
    try:
        tarea_completada = session.get(Tarea, tarea_id)
        if tarea_completada is None:
            raise NotFoundError(f"La tarea {tarea_id} no existe.")
        if not tarea_completada.recurrente:
            return None

        nueva = Tarea(
            id=uuid.uuid4(),
            casa_id=tarea_completada.casa_id,
            nombre=tarea_completada.nombre,
            descripcion=tarea_completada.descripcion,
            puntos=tarea_completada.puntos,
            responsable_id=tarea_completada.responsable_id,
            fecha_prevista=_siguiente_fecha_prevista(
                tarea_completada.fecha_prevista, tarea_completada.frecuencia
            ),
            estado=EstadoTareaEnum.PENDIENTE,
            recurrente=True,
            frecuencia=tarea_completada.frecuencia,
        )
        session.add(nueva)
        session.commit()
        session.refresh(nueva)
        return nueva
    except NotFoundError:
        session.rollback()
        raise
    finally:
        session.close()


def listar_tareas(casa_id: UUID, estado: Optional[EstadoTareaEnum] = None):
    """Lista las tareas de una casa, opcionalmente filtradas por estado.

    No es una de las "Interfaces Produced" de T2 (ninguna spec hermana la
    consume), pero se agrega para que la ruta GET de T3 sea un adaptador
    delgado, igual que `listar_miembros` en la spec `casas-miembros`.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        query = session.query(Tarea).filter(Tarea.casa_id == casa_id)
        if estado is not None:
            query = query.filter(Tarea.estado == estado)
        return query.all()
    finally:
        session.close()


def obtener_tarea(casa_id: UUID, tarea_id: UUID) -> Tarea:
    """Obtiene una Tarea de una casa puntual; usada por T3 para devolver el
    estado actualizado tras un PATCH."""
    session = get_session()
    try:
        tarea = (
            session.query(Tarea)
            .filter(Tarea.casa_id == casa_id, Tarea.id == tarea_id)
            .one_or_none()
        )
        if tarea is None:
            raise NotFoundError(f"La tarea {tarea_id} no existe en la casa {casa_id}.")
        return tarea
    finally:
        session.close()


def listar_historial(casa_id: UUID):
    """Lista el `HistorialTarea` de una casa (REQ-008), conservando
    registros de miembros que luego fueron desactivados (TC-010) — no se
    filtra por `Miembro.activo`."""
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return (
            session.query(HistorialTarea)
            .join(Tarea, Tarea.id == HistorialTarea.tarea_id)
            .filter(Tarea.casa_id == casa_id)
            .order_by(HistorialTarea.completada_en.desc())
            .all()
        )
    finally:
        session.close()
