"""Rutas HTTP de Tareas, Ranking e Historial — adaptadores delgados sobre T2.

Mismo patrón que `casas.py`: ninguna regla de negocio vive aquí. El
"actor"/usuario autenticado se resuelve desde un JWT real vía
`resolver_actor_en_casa` (`src/api/dependencies.py`, spec
`usuarios-auth`) — ya no vía el header placeholder `X-Usuario-Id`.

Un único router (`tareas_router`, sin prefijo propio) expone las cinco
rutas del contrato de `00-overview.md`, para respetar la única interfaz
producida documentada en `run-plan.json` (un solo `APIRouter`).
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import resolver_actor_en_casa
from src.api.schemas import (
    HistorialTareaOut,
    LogroObtenidoOut,
    RankingEntryOut,
    TareaCreate,
    TareaEstadoUpdate,
    TareaOut,
)
from src.db.models.tarea import EstadoTareaEnum
from src.services.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from src.services.logro_service import listar_logros_obtenidos
from src.services.ranking_service import calcular_ranking
from src.services.tarea_service import (
    completar_tarea,
    crear_tarea,
    listar_historial,
    listar_tareas,
    obtener_tarea,
    procesar_recurrencia,
)

tareas_router = APIRouter(tags=["tareas"])


@tareas_router.post(
    "/casas/{casa_id}/tareas", response_model=TareaOut, status_code=status.HTTP_201_CREATED
)
def crear_tarea_endpoint(
    casa_id: UUID, payload: TareaCreate, actor: UUID = Depends(resolver_actor_en_casa)
):
    try:
        return crear_tarea(
            casa_id,
            payload.nombre,
            payload.puntos,
            descripcion=payload.descripcion,
            responsable_id=payload.responsable_id,
            fecha_prevista=payload.fecha_prevista,
            recurrente=payload.recurrente,
            frecuencia=payload.frecuencia,
            actor=actor,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tareas_router.get("/casas/{casa_id}/tareas", response_model=list[TareaOut])
def listar_tareas_endpoint(
    casa_id: UUID,
    estado: Optional[str] = None,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    estado_enum = None
    if estado is not None:
        try:
            estado_enum = EstadoTareaEnum(estado)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estado inválido: {estado!r}."
            ) from exc
    try:
        return listar_tareas(casa_id, estado_enum)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tareas_router.get("/casas/{casa_id}/tareas/historial", response_model=list[HistorialTareaOut])
def listar_historial_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        return listar_historial(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tareas_router.patch("/casas/{casa_id}/tareas/{tarea_id}", response_model=TareaOut)
def actualizar_estado_tarea_endpoint(
    casa_id: UUID,
    tarea_id: UUID,
    payload: TareaEstadoUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    if payload.estado != EstadoTareaEnum.COMPLETADA.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta spec solo soporta la transición de estado a 'completada'.",
        )
    try:
        # El actor completa en su propio nombre (o, si es Administrador,
        # habilita el flujo de "registrar en nombre de" a nivel de
        # servicio); el contrato HTTP de esta spec no expone un `miembroId`
        # separado en el body — ver Design Rationale de T3/T4.
        completar_tarea(tarea_id, actor, actor)
        procesar_recurrencia(tarea_id)
        return obtener_tarea(casa_id, tarea_id)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tareas_router.get("/casas/{casa_id}/ranking", response_model=list[RankingEntryOut])
def obtener_ranking_endpoint(
    casa_id: UUID,
    mes: Optional[str] = None,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return calcular_ranking(casa_id, mes=mes)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tareas_router.get("/casas/{casa_id}/logros", response_model=list[LogroObtenidoOut])
def listar_logros_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        return listar_logros_obtenidos(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
