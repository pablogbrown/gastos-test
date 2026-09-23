"""Rutas HTTP de Avatares y Créditos — adaptadores delgados sobre T1/T3.

Mismo patrón que `tareas.py`: ninguna regla de negocio vive aquí; el
actor autenticado se resuelve vía `resolver_actor_en_casa`.

Desviación deliberada del contrato literal de `spec.md` (Judgment, ver
`build-results.md`): spec.md describe estas rutas como
`/miembros/{miembro_id}/...`, sin `casa_id`. Esta spec las anida bajo
`/casas/{casa_id}/miembros/{miembro_id}/...` — igual que TODA otra ruta
autenticada de este proyecto (`tareas.py`/`casas.py`) — porque
`resolver_actor_en_casa` (spec `usuarios-auth`) exige un `casa_id` de la
URL para resolver el actor, y el proxy de Vite (`vite.config.ts`) solo
reenvía `/casas`/`/auth`, no `/miembros` suelto.

Las 3 rutas GET son legibles por cualquier miembro activo de la casa
(mismo criterio de apertura ya establecido para Ranking/Historial: nada
en esta app es privado por miembro). El PUT de selección es self-service:
solo el propio miembro puede cambiar SU avatar (REQ-004 no menciona
ningún override de Administrador, a diferencia de `completar_tarea`).
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import resolver_actor_en_casa
from src.api.schemas import AvatarPersonajeOut, AvatarSeleccionUpdate, CreditosOut
from src.services.avatar_service import (
    listar_avatares_disponibles,
    obtener_avatar_seleccionado,
    obtener_balance_creditos,
    seleccionar_avatar,
)
from src.services.exceptions import NotFoundError, PermissionDeniedError

avatares_router = APIRouter(tags=["avatares"])


@avatares_router.get(
    "/casas/{casa_id}/miembros/{miembro_id}/creditos", response_model=CreditosOut
)
def obtener_creditos_endpoint(
    casa_id: UUID, miembro_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)
):
    return CreditosOut(saldo=obtener_balance_creditos(miembro_id))


@avatares_router.get(
    "/casas/{casa_id}/miembros/{miembro_id}/avatares-disponibles",
    response_model=list[AvatarPersonajeOut],
)
def listar_avatares_disponibles_endpoint(
    casa_id: UUID, miembro_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)
):
    try:
        return listar_avatares_disponibles(miembro_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@avatares_router.get(
    "/casas/{casa_id}/miembros/{miembro_id}/avatar",
    response_model=Optional[AvatarPersonajeOut],
)
def obtener_avatar_endpoint(
    casa_id: UUID, miembro_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)
):
    return obtener_avatar_seleccionado(miembro_id)


@avatares_router.put(
    "/casas/{casa_id}/miembros/{miembro_id}/avatar", response_model=AvatarPersonajeOut
)
def seleccionar_avatar_endpoint(
    casa_id: UUID,
    miembro_id: UUID,
    payload: AvatarSeleccionUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    if actor != miembro_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el propio miembro puede elegir su avatar.",
        )
    try:
        seleccionar_avatar(miembro_id, payload.avatar_personaje_id)
        return obtener_avatar_seleccionado(miembro_id)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
