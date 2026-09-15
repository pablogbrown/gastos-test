"""Rutas HTTP de TarjetaCredito — adaptador delgado sobre T2
(`tarjeta_service`).

Ninguna regla de negocio vive aquí: cada handler valida forma (vía
Pydantic), delega en el servicio correspondiente y traduce las
excepciones de dominio a códigos HTTP, siguiendo el mismo patrón que
`src/api/routes/suscripciones.py`.

Router propio (no agregado a otro archivo) — mismo criterio que separó
`casas.py`/`gastos.py`/`tareas.py`/`suscripciones.py`/`dashboard.py`
entre sí: un recurso HTTP por módulo, todos bajo el prefijo compartido
`/casas`.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.dependencies import resolver_actor_en_casa
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.tarjeta_service import (
    actualizar_tarjeta,
    crear_tarjeta,
    eliminar_tarjeta,
    listar_tarjetas,
)

tarjetas_router = APIRouter(prefix="/casas", tags=["tarjetas"])


class TarjetaCreate(BaseModel):
    banco: Optional[str] = None
    nombre: Optional[str] = None
    ultimos_digitos: Optional[str] = None
    fecha_cierre_actual: Optional[date] = None
    fecha_vencimiento_actual: Optional[date] = None


class TarjetaUpdate(BaseModel):
    # Todos opcionales (REQ-002): solo se actualizan los campos provistos.
    fecha_cierre_actual: Optional[date] = None
    fecha_vencimiento_actual: Optional[date] = None
    saldo_actual_ars: Optional[Decimal] = None
    saldo_actual_usd: Optional[Decimal] = None


class TarjetaOut(BaseModel):
    id: UUID
    casa_id: UUID
    miembro_id: UUID
    banco: str
    nombre: str
    ultimos_digitos: str
    fecha_cierre_actual: date
    fecha_vencimiento_actual: date
    saldo_actual_ars: Optional[Decimal] = None
    saldo_actual_usd: Optional[Decimal] = None
    activa: bool
    creado_en: datetime

    class Config:
        orm_mode = True


class TarjetaAlertaOut(BaseModel):
    id: UUID
    nombre: str
    banco: str
    fecha_vencimiento_actual: date
    dias_para_vencimiento: int
    vencida: bool

    class Config:
        orm_mode = True


@tarjetas_router.post(
    "/{casa_id}/tarjetas",
    response_model=TarjetaOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_tarjeta_endpoint(
    casa_id: UUID,
    payload: TarjetaCreate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return crear_tarjeta(
            casa_id,
            actor,
            payload.banco,
            payload.nombre,
            payload.ultimos_digitos,
            payload.fecha_cierre_actual,
            payload.fecha_vencimiento_actual,
            actor,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tarjetas_router.get("/{casa_id}/tarjetas", response_model=list[TarjetaOut])
def listar_tarjetas_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        return listar_tarjetas(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tarjetas_router.patch("/{casa_id}/tarjetas/{tarjeta_id}", response_model=TarjetaOut)
def actualizar_tarjeta_endpoint(
    casa_id: UUID,
    tarjeta_id: UUID,
    payload: TarjetaUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return actualizar_tarjeta(
            casa_id,
            tarjeta_id,
            actor,
            fecha_cierre_actual=payload.fecha_cierre_actual,
            fecha_vencimiento_actual=payload.fecha_vencimiento_actual,
            saldo_actual_ars=payload.saldo_actual_ars,
            saldo_actual_usd=payload.saldo_actual_usd,
        )
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@tarjetas_router.delete(
    "/{casa_id}/tarjetas/{tarjeta_id}", status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_tarjeta_endpoint(
    casa_id: UUID,
    tarjeta_id: UUID,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        eliminar_tarjeta(casa_id, tarjeta_id, actor)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
