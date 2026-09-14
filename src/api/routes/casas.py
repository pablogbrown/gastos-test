"""Rutas HTTP de Casas y Miembros — adaptadores delgados sobre T2.

Ninguna regla de negocio vive aquí: cada handler valida forma (vía
Pydantic), delega en el servicio correspondiente y traduce las
excepciones de dominio a códigos HTTP.

Nota de diseño (spec `usuarios-auth`): el "actor"/usuario autenticado ya
no se recibe vía el header placeholder `X-Usuario-Id` (aceptaba
cualquier UUID sin verificar identidad) — se resuelve desde un JWT real
(`Authorization: Bearer <token>`) vía las dependencies de
`src/api/dependencies.py`. `crear_casa_endpoint` (no hay Casa todavía)
usa `get_current_usuario` directo; el resto usa `resolver_actor_en_casa`,
que además valida que el Usuario tenga un Miembro activo en la Casa de la
ruta (REQ-005) antes de delegar en los servicios de T2, que no cambian.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_usuario, resolver_actor_en_casa
from src.api.schemas import CasaCreate, CasaOut, MiembroActivoUpdate, MiembroCreate, MiembroOut
from src.services.casa_service import crear_casa, listar_casas_de_usuario
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import agregar_miembro, desactivar_miembro, listar_miembros

casas_router = APIRouter(prefix="/casas", tags=["casas"])


@casas_router.post("", response_model=CasaOut, status_code=status.HTTP_201_CREATED)
def crear_casa_endpoint(payload: CasaCreate, usuario_id: UUID = Depends(get_current_usuario)):
    try:
        casa = crear_casa(payload.nombre, usuario_id)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return casa


@casas_router.get("/mias", response_model=list[CasaOut])
def listar_casas_mias_endpoint(usuario_id: UUID = Depends(get_current_usuario)):
    """REQ-006/TC-010: las Casas donde el Usuario autenticado tiene un
    Miembro activo — declarada antes de `/{casa_id}/...` para no competir
    con esas rutas parametrizadas (aunque `mias` no matchea su forma de
    todos modos, al no tener un sub-segmento adicional)."""
    return listar_casas_de_usuario(usuario_id)


@casas_router.post(
    "/{casa_id}/miembros", response_model=MiembroOut, status_code=status.HTTP_201_CREATED
)
def agregar_miembro_endpoint(
    casa_id: UUID, payload: MiembroCreate, actor: UUID = Depends(resolver_actor_en_casa)
):
    try:
        return agregar_miembro(casa_id, payload.nombre, payload.identificacion, payload.email, actor)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@casas_router.patch("/{casa_id}/miembros/{miembro_id}", response_model=MiembroOut)
def actualizar_miembro_endpoint(
    casa_id: UUID,
    miembro_id: UUID,
    payload: MiembroActivoUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    if payload.activo:
        # T2 solo produce `desactivar_miembro`; reactivar un miembro no es
        # parte del contrato de esta spec.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reactivar un miembro no está soportado por esta spec.",
        )
    try:
        return desactivar_miembro(casa_id, miembro_id, actor)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@casas_router.get("/{casa_id}/miembros", response_model=list[MiembroOut])
def listar_miembros_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        return listar_miembros(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
