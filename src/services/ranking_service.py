"""Servicio de Ranking: puntos acumulados por miembro (REQ-005, REQ-006),
más niveles, rachas y ranking por mes (spec `gamificacion-puntos`).

Vista de solo lectura, separada de `tarea_service` por SRP: el ranking
agrega `HistorialTarea` sin acoplarse a la lógica de mutación de tareas.
No se guarda un contador de puntos separado en `Miembro` — el ranking se
deriva íntegramente del historial para evitar desincronización.
"""
import calendar
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import func

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.historial_tarea import HistorialTarea
from src.db.models.tarea import Tarea
from src.services.exceptions import NotFoundError, ValidationError

# Spec `gamificacion-puntos`, REQ-001: 4 escalones fijos, derivados del
# total de puntos HISTÓRICO de un miembro (nunca del total filtrado por
# mes — el nivel es un logro acumulado de siempre, ver `00-overview.md`).
NIVELES = [
    (0, "Novato"),
    (50, "Activo"),
    (150, "Comprometido"),
    (300, "Campeón de la casa"),
]


def _nivel_de(puntos_totales: int) -> str:
    nivel = NIVELES[0][1]
    for umbral, nombre in NIVELES:
        if puntos_totales >= umbral:
            nivel = nombre
    return nivel


def _rango_mes(mes: str) -> Tuple[datetime, datetime]:
    """Resuelve `mes` (`YYYY-MM`) al rango datetime [primer día 00:00,
    último día 23:59:59.999999] de ese mes — copia local deliberada de
    `gasto_service._rango_mes`/`balance_service._rango_mes` (mismo
    criterio de "un servicio por responsabilidad" ya establecido en
    `[SERVP-02]`, no se importa la de `gasto_service.py`).

    A diferencia de esas dos, acá el rango se expresa en `datetime` (no
    `date`) porque `HistorialTarea.completada_en` es una columna
    `DateTime`, no `Date`.
    """
    try:
        anio, numero_mes = (int(parte) for parte in mes.split("-"))
        if not (1 <= numero_mes <= 12):
            raise ValueError
    except ValueError as exc:
        raise ValidationError(f"Formato de mes inválido: {mes!r}. Se espera 'YYYY-MM'.") from exc
    ultimo_dia = calendar.monthrange(anio, numero_mes)[1]
    desde = datetime.combine(date(anio, numero_mes, 1), time.min)
    hasta = datetime.combine(date(anio, numero_mes, ultimo_dia), time.max)
    return desde, hasta


def calcular_racha(casa_id: UUID, miembro_id: UUID) -> int:
    """Días consecutivos (calendario, UTC) con al menos un `HistorialTarea`
    de `miembro_id` en `casa_id`, contando hacia atrás desde hoy o ayer
    (REQ-002). Completar más de una tarea el mismo día cuenta como un solo
    día (TC-003); un día sin actividad corta la racha ahí mismo, sin
    seguir contando actividad más antigua.

    Sin noción de zona horaria de la casa en ningún otro lado del
    proyecto (todas las fechas ya son ingenuas) — UTC es el mismo
    criterio simple ya usado en el resto de la app, no una inconsistencia
    nueva (ver Tradeoffs, `00-overview.md`).
    """
    session = get_session()
    try:
        filas = (
            session.query(HistorialTarea.completada_en)
            .join(Tarea, Tarea.id == HistorialTarea.tarea_id)
            .filter(Tarea.casa_id == casa_id, HistorialTarea.miembro_id == miembro_id)
            .all()
        )
        dias = sorted({fila.completada_en.date() for fila in filas}, reverse=True)
        if not dias:
            return 0

        hoy = datetime.now(timezone.utc).date()
        if dias[0] not in (hoy, hoy - timedelta(days=1)):
            return 0

        racha = 1
        dia_actual = dias[0]
        for dia in dias[1:]:
            if dia_actual - dia == timedelta(days=1):
                racha += 1
                dia_actual = dia
            else:
                break
        return racha
    finally:
        session.close()


def calcular_ranking(casa_id: UUID, mes: Optional[str] = None) -> list:
    """Agrega los puntos obtenidos por cada miembro de `casa_id` a partir de
    `HistorialTarea`, ordenados de mayor a menor puntaje (TC-007, TC-008).

    Incluye miembros desactivados con puntos históricos — no se filtra por
    `Miembro.activo` (REQ-005, REQ-008).

    `mes` (spec `gamificacion-puntos`, REQ-003): `None` (default) preserva
    el comportamiento 100% actual — todos los puntos históricos de la
    casa, sin filtro. `dashboard_service.armar_dashboard` sigue llamando
    esta función sin `mes`, así que su comportamiento no cambia
    (regresión, TC-004). Con `mes`, solo se agregan los puntos de tareas
    completadas ese mes — pero `nivel` (más abajo) sigue calculándose
    sobre el total HISTÓRICO de cada miembro, nunca sobre el filtrado.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        query = (
            session.query(
                HistorialTarea.miembro_id,
                func.sum(HistorialTarea.puntos_obtenidos).label("puntos"),
            )
            .join(Tarea, Tarea.id == HistorialTarea.tarea_id)
            .filter(Tarea.casa_id == casa_id)
        )
        if mes is not None:
            desde, hasta = _rango_mes(mes)
            query = query.filter(HistorialTarea.completada_en.between(desde, hasta))

        filas = query.group_by(HistorialTarea.miembro_id).order_by(
            func.sum(HistorialTarea.puntos_obtenidos).desc()
        ).all()

        # El nivel se calcula sobre el total HISTÓRICO de cada miembro,
        # nunca sobre el total filtrado por mes — se resuelve con una
        # segunda agregación sin filtro de mes (00-overview.md).
        totales_historicos = dict(
            session.query(
                HistorialTarea.miembro_id,
                func.sum(HistorialTarea.puntos_obtenidos),
            )
            .join(Tarea, Tarea.id == HistorialTarea.tarea_id)
            .filter(Tarea.casa_id == casa_id)
            .group_by(HistorialTarea.miembro_id)
            .all()
        )

        resultado = []
        for fila in filas:
            puntos_historicos = int(totales_historicos.get(fila.miembro_id, 0))
            resultado.append(
                {
                    "miembroId": fila.miembro_id,
                    "puntos": int(fila.puntos),
                    "nivel": _nivel_de(puntos_historicos),
                    "racha": calcular_racha(casa_id, fila.miembro_id),
                }
            )
        return resultado
    finally:
        session.close()
