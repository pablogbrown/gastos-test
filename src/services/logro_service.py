"""Servicio de Logros: catálogo fijo de logros desbloqueables sobre el
progreso ya derivado de `HistorialTarea` (spec `gamificacion-puntos`,
REQ-004).

Ningún logro se puede configurar desde afuera de este archivo — el
catálogo es fijo en código (`LOGROS_CATALOGO`), no una tabla editable
(ver Tradeoffs, `00-overview.md`).
"""
import uuid
from typing import List
from uuid import UUID

from sqlalchemy import func

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.historial_tarea import HistorialTarea
from src.db.models.logro_obtenido import LogroObtenido
from src.db.models.tarea import Tarea
from src.services.exceptions import NotFoundError
from src.services.ranking_service import calcular_racha

LOGROS_CATALOGO = [
    {"id": "primera_tarea", "nombre": "Primera tarea", "tipo": "tareas", "umbral": 1},
    {"id": "diez_tareas", "nombre": "10 tareas completadas", "tipo": "tareas", "umbral": 10},
    {"id": "cincuenta_tareas", "nombre": "50 tareas completadas", "tipo": "tareas", "umbral": 50},
    {"id": "cien_puntos", "nombre": "100 puntos", "tipo": "puntos", "umbral": 100},
    {"id": "quinientos_puntos", "nombre": "500 puntos", "tipo": "puntos", "umbral": 500},
    {"id": "racha_siete", "nombre": "Racha de 7 días", "tipo": "racha", "umbral": 7},
    {"id": "racha_treinta", "nombre": "Racha de 30 días", "tipo": "racha", "umbral": 30},
]


def evaluar_logros(casa_id: UUID, miembro_id: UUID) -> List[LogroObtenido]:
    """Evalúa `LOGROS_CATALOGO` para `miembro_id` en `casa_id` (cantidad de
    tareas completadas, puntos totales, racha — todo derivado de
    `HistorialTarea`/`ranking_service.calcular_racha`) y persiste los
    logros nuevos que corresponden.

    El chequeo de "ya existe" ocurre acá, en el service layer, ANTES de
    cualquier insert — nunca vía un constraint `UNIQUE` de base de datos
    ([SERV-01], `.nybo/memory/domains/services.md`) — así que llamar esta
    función más de una vez para el mismo estado nunca duplica un logro.
    Devuelve solo los logros NUEVOS desbloqueados en esta llamada (lista
    vacía si no hay ninguno)."""
    session = get_session()
    try:
        total_tareas = (
            session.query(func.count(HistorialTarea.id))
            .join(Tarea, Tarea.id == HistorialTarea.tarea_id)
            .filter(Tarea.casa_id == casa_id, HistorialTarea.miembro_id == miembro_id)
            .scalar()
            or 0
        )
        total_puntos = (
            session.query(func.sum(HistorialTarea.puntos_obtenidos))
            .join(Tarea, Tarea.id == HistorialTarea.tarea_id)
            .filter(Tarea.casa_id == casa_id, HistorialTarea.miembro_id == miembro_id)
            .scalar()
            or 0
        )
        racha = calcular_racha(casa_id, miembro_id)

        valores_por_tipo = {"tareas": total_tareas, "puntos": int(total_puntos), "racha": racha}

        ya_obtenidos = {
            fila.logro_id
            for fila in session.query(LogroObtenido.logro_id).filter(
                LogroObtenido.casa_id == casa_id, LogroObtenido.miembro_id == miembro_id
            )
        }

        nuevos = []
        for logro in LOGROS_CATALOGO:
            if logro["id"] in ya_obtenidos:
                continue
            if valores_por_tipo[logro["tipo"]] >= logro["umbral"]:
                fila = LogroObtenido(
                    id=uuid.uuid4(),
                    casa_id=casa_id,
                    miembro_id=miembro_id,
                    logro_id=logro["id"],
                )
                session.add(fila)
                nuevos.append(fila)

        if nuevos:
            session.commit()
            for fila in nuevos:
                session.refresh(fila)
        return nuevos
    finally:
        session.close()


def listar_logros_obtenidos(casa_id: UUID) -> List[LogroObtenido]:
    """Todos los logros desbloqueados de `casa_id`, para que el frontend
    arme "estos son los logros de cada miembro" sin pedir uno por uno."""
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return (
            session.query(LogroObtenido)
            .filter(LogroObtenido.casa_id == casa_id)
            .order_by(LogroObtenido.obtenido_en.desc())
            .all()
        )
    finally:
        session.close()
