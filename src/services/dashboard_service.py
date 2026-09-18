"""Servicio de Dashboard: agregación de solo lectura para la pantalla
principal de una Casa (REQ-001).

`dashboard_service` no persiste datos propios ni duplica lógica de
negocio ya resuelta en `balance_service`/`ranking_service` — agrega en
tiempo real lo que esos servicios (y `gasto_service`/`tarea_service`) ya
calculan, evitando una segunda fuente de verdad para esos cálculos.
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional
from uuid import UUID

from src.db.models.gasto import Gasto
from src.db.models.historial_tarea import HistorialTarea
from src.db.models.miembro import Miembro
from src.db.models.tarea import EstadoTareaEnum, Tarea
from src.services.balance_service import BalanceCasa, calcular_balance
from src.services.gasto_service import listar_gastos
from src.services.mantenimiento_service import (
    ItemMantenimientoAlerta,
    obtener_items_con_alerta,
)
from src.services.miembro_service import listar_miembros
from src.services.ranking_service import calcular_progreso_meta, calcular_ranking
from src.services.tarea_service import listar_historial, listar_tareas
from src.services.tarjeta_service import TarjetaAlerta, obtener_tarjetas_con_alerta

_LIMITE_RECIENTES = 10


@dataclass
class DashboardCasa:
    """Estado agregado de una Casa para su pantalla principal (REQ-001)."""

    miembros: List[Miembro] = field(default_factory=list)
    gastos_recientes: List[Gasto] = field(default_factory=list)
    balance: BalanceCasa = field(default_factory=lambda: BalanceCasa(totales=[], aportes=[]))
    tareas_pendientes: List[Tarea] = field(default_factory=list)
    tareas_completadas_recientes: List[HistorialTarea] = field(default_factory=list)
    ranking: List[dict] = field(default_factory=list)
    # Spec `tarjetas-credito`, REQ-004: tarjetas activas de la casa cuyo
    # vencimiento está a `UMBRAL_ALERTA_DIAS` días o menos (o ya venció).
    tarjetas_con_alerta: List[TarjetaAlerta] = field(default_factory=list)
    # Spec `mantenimiento-casa`, REQ-005: ítems de mantenimiento pendientes
    # cuya fecha estimada está a `UMBRAL_ALERTA_DIAS` días o menos (o ya
    # vencidos) — mismo criterio que `tarjetas_con_alerta`.
    mantenimiento_con_alerta: List[ItemMantenimientoAlerta] = field(default_factory=list)
    # Spec `gamificacion-puntos`, REQ-005: progreso de la casa contra su
    # meta de puntos mensual — `None` cuando no hay meta configurada
    # (mismo criterio que `tarjetas_con_alerta`: aditivo, no rompe una
    # casa sin la nueva funcionalidad configurada).
    meta_casa: Optional[dict] = None


def armar_dashboard(casa_id: UUID) -> DashboardCasa:
    """Agrega el estado general de `casa_id` para su pantalla principal:
    miembros activos, últimos 10 gastos, balance, tareas pendientes,
    últimas 10 tareas completadas y ranking de puntos.

    Cada sección queda vacía (no lanza error) si la casa todavía no tiene
    gastos ni tareas registrados (TC-002); solo propaga `NotFoundError`
    (vía la primera consulta, `listar_miembros`) si `casa_id` no
    corresponde a ninguna casa existente.
    """
    miembros = [miembro for miembro in listar_miembros(casa_id) if miembro.activo]
    gastos_recientes = listar_gastos(casa_id)[:_LIMITE_RECIENTES]
    balance = calcular_balance(casa_id)
    tareas_pendientes = listar_tareas(casa_id, EstadoTareaEnum.PENDIENTE)
    tareas_completadas_recientes = listar_historial(casa_id)[:_LIMITE_RECIENTES]
    ranking = calcular_ranking(casa_id)
    tarjetas_con_alerta = obtener_tarjetas_con_alerta(casa_id)
    mantenimiento_con_alerta = obtener_items_con_alerta(casa_id)
    mes_actual = date.today().strftime("%Y-%m")
    meta_casa = calcular_progreso_meta(casa_id, mes_actual)

    return DashboardCasa(
        miembros=miembros,
        gastos_recientes=gastos_recientes,
        balance=balance,
        tareas_pendientes=tareas_pendientes,
        tareas_completadas_recientes=tareas_completadas_recientes,
        ranking=ranking,
        tarjetas_con_alerta=tarjetas_con_alerta,
        mantenimiento_con_alerta=mantenimiento_con_alerta,
        meta_casa=meta_casa,
    )
