"""Servicio de Actividad: registro append-only de eventos relevantes de
una Casa (REQ-002, REQ-003).

`registrar_actividad` se invoca como hook directo desde
`gasto_service.registrar_gasto` y desde `tarea_service.crear_tarea`/
`completar_tarea`, siempre después de que la operación correspondiente ya
confirmó su propia transacción (nunca antes) — así una entrada de
actividad nunca describe algo que en definitiva no llegó a ocurrir.
"""
import uuid
from typing import List, Optional, Union
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.historial_actividad import HistorialActividad, TipoActividadEnum
from src.services.exceptions import NotFoundError


def registrar_actividad(
    casa_id: UUID,
    tipo: Union[TipoActividadEnum, str],
    miembro_id: Optional[UUID],
    descripcion: str,
) -> HistorialActividad:
    """Inserta una entrada en `historial_actividad` (REQ-002).

    No revalida membresía ni permisos: el llamador (`gasto_service`,
    `tarea_service`) ya validó por su cuenta la operación de negocio que
    originó el evento; este hook solo persiste el registro resultante.
    """
    tipo_enum = tipo if isinstance(tipo, TipoActividadEnum) else TipoActividadEnum(tipo)

    session = get_session()
    try:
        entrada = HistorialActividad(
            id=uuid.uuid4(),
            casa_id=casa_id,
            tipo=tipo_enum,
            miembro_id=miembro_id,
            descripcion=descripcion,
        )
        session.add(entrada)
        session.commit()
        session.refresh(entrada)
        return entrada
    finally:
        session.close()


def obtener_actividad(casa_id: UUID) -> List[HistorialActividad]:
    """Historial de actividad de una casa, del más reciente al más
    antiguo (REQ-003, TC-005). Consultable por cualquier miembro — la
    membresía se valida a nivel de ruta (T3), no aquí."""
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return (
            session.query(HistorialActividad)
            .filter(HistorialActividad.casa_id == casa_id)
            .order_by(HistorialActividad.fecha.desc())
            .all()
        )
    finally:
        session.close()
