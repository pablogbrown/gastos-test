"""Rutas HTTP de Auto — adaptador delgado sobre T2 (`auto_service`).

Ninguna regla de negocio vive aquí: cada handler valida forma (vía
Pydantic), delega en el servicio correspondiente y traduce las
excepciones de dominio a códigos HTTP, siguiendo el mismo patrón que
`src/api/routes/tarjetas.py`.

Router propio (no agregado a otro archivo) — mismo criterio que separó
cada recurso HTTP en su propio módulo a lo largo del proyecto. Sin
edición ni borrado en esta spec — alta y listado alcanzan (ver
`00-overview.md`'s API/Data Contracts).
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.dependencies import resolver_actor_en_casa
from src.services.auto_service import crear_auto, listar_autos
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError

autos_router = APIRouter(prefix="/casas", tags=["autos"])


class AutoCreate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    patente: Optional[str] = None
    anio: Optional[int] = None


class AutoOut(BaseModel):
    id: UUID
    casa_id: UUID
    marca: str
    modelo: str
    patente: Optional[str] = None
    anio: Optional[int] = None
    creado_en: datetime

    class Config:
        orm_mode = True


@autos_router.post(
    "/{casa_id}/autos",
    response_model=AutoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_auto_endpoint(
    casa_id: UUID,
    payload: AutoCreate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return crear_auto(
            casa_id,
            payload.marca,
            payload.modelo,
            actor,
            patente=payload.patente,
            anio=payload.anio,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@autos_router.get("/{casa_id}/autos", response_model=List[AutoOut])
def listar_autos_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        return listar_autos(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
