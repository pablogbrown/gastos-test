"""Rutas HTTP de Casas y Miembros — adaptadores delgados sobre T2.

Ninguna regla de negocio vive aquí: cada handler valida forma (vía
Pydantic), delega en el servicio correspondiente y traduce las
excepciones de dominio a códigos HTTP.

Nota de diseño (auth pendiente): esta spec no incluye el dominio `auth`
(fuera de alcance — ver spec.md). Mientras no exista, el "actor"/usuario
autenticado se recibe vía el header `X-Usuario-Id`, que una spec de auth
futura reemplazará por la identidad resuelta de una sesión/token real sin
cambiar la forma de los servicios de T2 que ya reciben un `actor: UUID`.
"""
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from src.api.schemas import CasaCreate, CasaOut, MiembroActivoUpdate, MiembroCreate, MiembroOut
from src.services.casa_service import crear_casa
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import agregar_miembro, desactivar_miembro, listar_miembros

casas_router = APIRouter(prefix="/casas", tags=["casas"])


def _usuario_id(x_usuario_id: UUID = Header(..., alias="X-Usuario-Id")) -> UUID:
    return x_usuario_id


@casas_router.post("", response_model=CasaOut, status_code=status.HTTP_201_CREATED)
def crear_casa_endpoint(payload: CasaCreate, usuario_id: UUID = Header(..., alias="X-Usuario-Id")):
    try:
        casa = crear_casa(payload.nombre, usuario_id)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return casa


@casas_router.post(
    "/{casa_id}/miembros", response_model=MiembroOut, status_code=status.HTTP_201_CREATED
)
def agregar_miembro_endpoint(
    casa_id: UUID, payload: MiembroCreate, actor: UUID = Header(..., alias="X-Usuario-Id")
):
    try:
        return agregar_miembro(casa_id, payload.nombre, payload.identificacion, actor)
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
    actor: UUID = Header(..., alias="X-Usuario-Id"),
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
def listar_miembros_endpoint(casa_id: UUID, actor: UUID = Header(..., alias="X-Usuario-Id")):
    try:
        return listar_miembros(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
