"""Rutas HTTP de Dashboard y Actividad — adaptadores delgados sobre T2
(`dashboard_service`, `actividad_service`).

Mismo patrón que el resto de los routers de esta feature (`casas.py`,
`tareas.py`, `gastos.py`): ninguna regla de negocio vive aquí. El
"actor"/usuario autenticado se resuelve desde un JWT real vía
`resolver_actor_en_casa` (`src/api/dependencies.py`, spec
`usuarios-auth`) — ya no vía el header placeholder `X-Usuario-Id`. Son
rutas de solo lectura sin guard de rol adicional más allá de membresía
activa: cualquier miembro puede consultarlas (REQ-003).

Los esquemas de respuesta de las secciones ya existentes (miembros,
gastos, balance, tareas, ranking) se reutilizan de `src.api.schemas` y de
`src.api.routes.gastos` en vez de redefinirse, para no divergir de los
contratos ya fijados por las specs `casas-miembros`/`gastos`/
`tareas-puntos`.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.dependencies import resolver_actor_en_casa
from src.api.routes.gastos import BalancePorMiembroOut, GastoOut
from src.api.routes.tarjetas import TarjetaAlertaOut
from src.api.schemas import HistorialTareaOut, MiembroOut, RankingEntryOut, TareaOut
from src.services.actividad_service import obtener_actividad
from src.services.dashboard_service import armar_dashboard
from src.services.exceptions import NotFoundError

dashboard_router = APIRouter(prefix="/casas", tags=["dashboard"])


class DashboardOut(BaseModel):
    """Contrato de `GET /casas/{casaId}/inicio` (00-overview.md)."""

    miembros: List[MiembroOut]
    gastos_recientes: List[GastoOut] = Field(default_factory=list, alias="gastosRecientes")
    balance: List[BalancePorMiembroOut] = Field(default_factory=list)
    tareas_pendientes: List[TareaOut] = Field(default_factory=list, alias="tareasPendientes")
    tareas_completadas_recientes: List[HistorialTareaOut] = Field(
        default_factory=list, alias="tareasCompletadasRecientes"
    )
    ranking: List[RankingEntryOut] = Field(default_factory=list)
    # Spec `tarjetas-credito`, REQ-004 (aditivo).
    tarjetas_con_alerta: List[TarjetaAlertaOut] = Field(
        default_factory=list, alias="tarjetasConAlerta"
    )

    class Config:
        allow_population_by_field_name = True


class ActividadOut(BaseModel):
    """Contrato de `GET /casas/{casaId}/actividad` (00-overview.md)."""

    id: UUID
    casa_id: UUID
    tipo: str
    miembro_id: Optional[UUID] = None
    fecha: datetime
    descripcion: str

    class Config:
        orm_mode = True


@dashboard_router.get("/{casa_id}/inicio", response_model=DashboardOut)
def obtener_inicio_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        dashboard = armar_dashboard(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DashboardOut(
        miembros=dashboard.miembros,
        gastos_recientes=dashboard.gastos_recientes,
        balance=dashboard.balance,
        tareas_pendientes=dashboard.tareas_pendientes,
        tareas_completadas_recientes=dashboard.tareas_completadas_recientes,
        ranking=dashboard.ranking,
        tarjetas_con_alerta=dashboard.tarjetas_con_alerta,
    )


@dashboard_router.get("/{casa_id}/actividad", response_model=List[ActividadOut])
def obtener_actividad_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        return obtener_actividad(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
