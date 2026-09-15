"""Rutas HTTP de Suscripciones — adaptador delgado sobre T2
(`suscripcion_service`).

Ninguna regla de negocio vive aquí: cada handler valida forma (vía
Pydantic), delega en el servicio correspondiente y traduce las
excepciones de dominio a códigos HTTP, siguiendo el mismo patrón que
`src/api/routes/casas.py`/`gastos.py`/`tareas.py`.

Archivo de ruta propio (no agregado a `gastos.py`) — mismo criterio que
separó `casas.py`/`gastos.py`/`tareas.py`/`dashboard.py` entre sí: cada
recurso HTTP en su propio módulo, todos bajo el prefijo compartido
`/casas`.
"""
from decimal import Decimal
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.dependencies import resolver_actor_en_casa
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.suscripcion_service import (
    cancelar_suscripcion,
    crear_suscripcion,
    listar_suscripciones,
)

suscripciones_router = APIRouter(prefix="/casas", tags=["suscripciones"])


class SuscripcionCreate(BaseModel):
    descripcion: str
    importe: Decimal
    # Optional a nivel de esquema (en vez de requerido) para que un
    # payload sin `categoria_id` llegue al servicio y sea rechazado con
    # 400 vía `ValidationError`, mismo criterio que `GastoCreate`.
    categoria_id: Optional[UUID] = None


class SuscripcionActivaUpdate(BaseModel):
    activa: bool


class SuscripcionOut(BaseModel):
    id: UUID
    casa_id: UUID
    descripcion: str
    importe: Decimal
    categoria_id: UUID
    pagado_por: UUID
    activa: bool
    ultimo_mes_generado: Optional[str] = None
    creado_en: datetime

    class Config:
        orm_mode = True


@suscripciones_router.post(
    "/{casa_id}/suscripciones",
    response_model=SuscripcionOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_suscripcion_endpoint(
    casa_id: UUID,
    payload: SuscripcionCreate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return crear_suscripcion(
            casa_id, payload.descripcion, payload.importe, payload.categoria_id, actor
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@suscripciones_router.get("/{casa_id}/suscripciones", response_model=list[SuscripcionOut])
def listar_suscripciones_endpoint(
    casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)
):
    try:
        return listar_suscripciones(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@suscripciones_router.patch(
    "/{casa_id}/suscripciones/{suscripcion_id}", response_model=SuscripcionOut
)
def actualizar_suscripcion_endpoint(
    casa_id: UUID,
    suscripcion_id: UUID,
    payload: SuscripcionActivaUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    if payload.activa:
        # `suscripcion_service` solo produce `cancelar_suscripcion`;
        # reactivar una suscripción no es parte del contrato de esta spec
        # — mismo criterio que `actualizar_miembro_endpoint`.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reactivar una suscripción no está soportado.",
        )
    try:
        return cancelar_suscripcion(casa_id, suscripcion_id, actor)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
