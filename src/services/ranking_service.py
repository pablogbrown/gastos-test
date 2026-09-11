"""Servicio de Ranking: puntos acumulados por miembro (REQ-005, REQ-006).

Vista de solo lectura, separada de `tarea_service` por SRP: el ranking
agrega `HistorialTarea` sin acoplarse a la lógica de mutación de tareas.
No se guarda un contador de puntos separado en `Miembro` — el ranking se
deriva íntegramente del historial para evitar desincronización.
"""
from uuid import UUID

from sqlalchemy import func

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.historial_tarea import HistorialTarea
from src.db.models.tarea import Tarea
from src.services.exceptions import NotFoundError


def calcular_ranking(casa_id: UUID) -> list:
    """Agrega los puntos obtenidos por cada miembro de `casa_id` a partir de
    `HistorialTarea`, ordenados de mayor a menor puntaje (TC-007, TC-008).

    Incluye miembros desactivados con puntos históricos — no se filtra por
    `Miembro.activo` (REQ-005, REQ-008).
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        filas = (
            session.query(
                HistorialTarea.miembro_id,
                func.sum(HistorialTarea.puntos_obtenidos).label("puntos"),
            )
            .join(Tarea, Tarea.id == HistorialTarea.tarea_id)
            .filter(Tarea.casa_id == casa_id)
            .group_by(HistorialTarea.miembro_id)
            .order_by(func.sum(HistorialTarea.puntos_obtenidos).desc())
            .all()
        )
        return [{"miembroId": fila.miembro_id, "puntos": int(fila.puntos)} for fila in filas]
    finally:
        session.close()
