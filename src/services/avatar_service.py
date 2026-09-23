"""Servicio de Avatares: economía de créditos, catálogo de razas y
selección (spec `avatares-economia`, REQ-001 a REQ-004).

Fundación de la que dependen `tienda-accesorios` (gasta créditos) y
`perfil-avatar-ui` (integra visualmente la selección). No toca ningún
archivo de `gamificacion-puntos` (puntos/ranking/logros/meta) — este
servicio solo LEE el nivel ya calculado (`ranking_service._nivel_de`
sobre el total histórico de puntos del miembro), nunca cambia cómo se
calcula.

Cada función pública abre y cierra su propia sesión (mismo patrón que
`ranking_service.calcular_ranking`/`actividad_service.obtener_actividad`)
— ninguna toma `session` como parámetro, porque ninguna se llama desde
dentro de la transacción de otro servicio ([SERVP-01] no aplica acá.
"""
import uuid
from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, or_

from src.db.base import get_session
from src.db.models.avatar_personaje import AvatarPersonaje
from src.db.models.credito_transaccion import CreditoTransaccion
from src.db.models.historial_tarea import HistorialTarea
from src.db.models.miembro import Miembro
from src.db.models.miembro_avatar_seleccionado import MiembroAvatarSeleccionado
from src.db.models.tarea import Tarea
from src.services.exceptions import NotFoundError, PermissionDeniedError
from src.services.ranking_service import NIVELES, _nivel_de

_ORDEN_NIVELES = [nombre for _umbral, nombre in NIVELES]


def _indice_nivel(nombre_nivel: str) -> int:
    """Posición de `nombre_nivel` en `ranking_service.NIVELES` (0 = el más
    bajo) — nunca se duplica el umbral numérico, solo se reusa el orden
    ya establecido por esa lista para comparar "menor o igual"."""
    return _ORDEN_NIVELES.index(nombre_nivel)


def obtener_balance_creditos(miembro_id: UUID) -> int:
    """Saldo de créditos de un miembro, derivado sumando sus
    `CreditoTransaccion` (REQ-001) — nunca un contador cacheado, mismo
    criterio que `ranking_service.calcular_ranking`. `0` si no hay
    ninguna fila todavía."""
    session = get_session()
    try:
        total = (
            session.query(func.sum(CreditoTransaccion.cantidad))
            .filter(CreditoTransaccion.miembro_id == miembro_id)
            .scalar()
        )
        return int(total or 0)
    finally:
        session.close()


def otorgar_creditos(casa_id: UUID, miembro_id: UUID, cantidad: int, motivo: str) -> CreditoTransaccion:
    """Registra una `CreditoTransaccion` a nombre de `miembro_id` (REQ-001).

    Hook llamado desde `tarea_service.completar_tarea`, en una
    transacción propia SEPARADA del `commit` que persiste
    `HistorialTarea` — mismo orden/criterio ya establecido para
    `registrar_actividad` ([SERV-02], `actividad_service.py`): nunca
    antes de que la operación disparadora ya haya confirmado la suya.
    """
    session = get_session()
    try:
        transaccion = CreditoTransaccion(
            id=uuid.uuid4(),
            casa_id=casa_id,
            miembro_id=miembro_id,
            cantidad=cantidad,
            motivo=motivo,
        )
        session.add(transaccion)
        session.commit()
        session.refresh(transaccion)
        return transaccion
    finally:
        session.close()


def listar_catalogo(miembro_id: UUID) -> List[AvatarPersonaje]:
    """Catálogo de razas de avatar seleccionable para `miembro_id` (REQ-002):
    toda raza cuya ventana de disponibilidad cubre hoy (o sin límite), MÁS
    la raza que `miembro_id` ya tenga seleccionada aunque esté fuera de
    ventana (TC-004's segunda mitad) — un miembro que ya la eligió la
    conserva sin verse afectado por el cierre de la ventana.
    """
    hoy = date.today()
    session = get_session()
    try:
        en_ventana = (
            session.query(AvatarPersonaje)
            .filter(
                or_(AvatarPersonaje.disponible_desde.is_(None), AvatarPersonaje.disponible_desde <= hoy),
                or_(AvatarPersonaje.disponible_hasta.is_(None), AvatarPersonaje.disponible_hasta >= hoy),
            )
            .all()
        )
        seleccion = session.get(MiembroAvatarSeleccionado, miembro_id)
        if seleccion is not None and seleccion.avatar_personaje_id not in {a.id for a in en_ventana}:
            ya_seleccionada = session.get(AvatarPersonaje, seleccion.avatar_personaje_id)
            if ya_seleccionada is not None:
                en_ventana.append(ya_seleccionada)
        return en_ventana
    finally:
        session.close()


def _nivel_actual_de(casa_id: UUID, miembro_id: UUID) -> str:
    """Nivel actual de un miembro (REQ-003), derivado en el momento del
    total histórico de puntos de `HistorialTarea` — nunca cacheado, y
    nunca duplicando el umbral de `ranking_service.NIVELES`/`_nivel_de`,
    que este servicio reusa tal cual."""
    session = get_session()
    try:
        total_puntos = (
            session.query(func.sum(HistorialTarea.puntos_obtenidos))
            .join(Tarea, Tarea.id == HistorialTarea.tarea_id)
            .filter(Tarea.casa_id == casa_id, HistorialTarea.miembro_id == miembro_id)
            .scalar()
        )
        return _nivel_de(int(total_puntos or 0))
    finally:
        session.close()


def listar_avatares_disponibles(miembro_id: UUID) -> List[AvatarPersonaje]:
    """Razas que `miembro_id` puede seleccionar HOY (REQ-003): el catálogo
    de `listar_catalogo` filtrado a `nivel_requerido <= nivel actual`, con
    el nivel recalculado en el momento (nunca cacheado) sobre el total
    histórico de puntos del miembro."""
    session = get_session()
    try:
        miembro = session.get(Miembro, miembro_id)
        if miembro is None:
            raise NotFoundError(f"El miembro {miembro_id} no existe.")
        casa_id = miembro.casa_id
    finally:
        session.close()

    indice_actual = _indice_nivel(_nivel_actual_de(casa_id, miembro_id))
    return [
        avatar
        for avatar in listar_catalogo(miembro_id)
        if _indice_nivel(avatar.nivel_requerido) <= indice_actual
    ]


def seleccionar_avatar(miembro_id: UUID, avatar_personaje_id: UUID) -> MiembroAvatarSeleccionado:
    """Selecciona/cambia el avatar de `miembro_id` (REQ-003/REQ-004):
    rechaza una raza que no esté en `listar_avatares_disponibles` (nivel
    insuficiente, o inexistente); si ya existe una selección, la
    reemplaza in-place — nunca acumula filas por miembro."""
    disponibles = {avatar.id for avatar in listar_avatares_disponibles(miembro_id)}
    if avatar_personaje_id not in disponibles:
        raise PermissionDeniedError(
            f"La raza {avatar_personaje_id} no está desbloqueada para este miembro."
        )

    session = get_session()
    try:
        seleccion = session.get(MiembroAvatarSeleccionado, miembro_id)
        if seleccion is None:
            seleccion = MiembroAvatarSeleccionado(
                miembro_id=miembro_id, avatar_personaje_id=avatar_personaje_id
            )
            session.add(seleccion)
        else:
            seleccion.avatar_personaje_id = avatar_personaje_id
        session.commit()
        session.refresh(seleccion)
        return seleccion
    finally:
        session.close()


def obtener_avatar_seleccionado(miembro_id: UUID) -> Optional[AvatarPersonaje]:
    """Avatar actualmente seleccionado por `miembro_id`, o `None` sin
    selección previa (REQ-004) — nunca se autoasigna una raza por
    defecto."""
    session = get_session()
    try:
        seleccion = session.get(MiembroAvatarSeleccionado, miembro_id)
        if seleccion is None:
            return None
        return session.get(AvatarPersonaje, seleccion.avatar_personaje_id)
    finally:
        session.close()
