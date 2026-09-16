"""Rutas HTTP de Prestamo — adaptador delgado sobre T2
(`prestamo_service`).

Ninguna regla de negocio vive aquí: cada handler valida forma (vía
Pydantic), delega en el servicio correspondiente y traduce las
excepciones de dominio a códigos HTTP, siguiendo el mismo patrón que
`src/api/routes/tarjetas.py`.

Router propio (no agregado a otro archivo) — mismo criterio que separó
`tarjetas.py`/`suscripciones.py`/`gastos.py` entre sí.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.dependencies import resolver_actor_en_casa
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.prestamo_service import (
    actualizar_estado_prestamo,
    confirmar_prestamo,
    crear_prestamo,
    listar_prestamos,
)

prestamos_router = APIRouter(prefix="/casas", tags=["prestamos"])


class PrestamoCreate(BaseModel):
    prestamista_id: UUID
    deudor_id: UUID
    importe: Decimal
    moneda: Optional[str] = "ARS"
    fecha: date
    descripcion: Optional[str] = None


class PrestamoEstadoUpdate(BaseModel):
    estado: str


class PrestamoConfirmacionUpdate(BaseModel):
    confirma: bool


class PrestamoOut(BaseModel):
    id: UUID
    casa_id: UUID
    prestamista_id: UUID
    deudor_id: UUID
    importe: Decimal
    moneda: str
    descripcion: Optional[str] = None
    fecha: date
    estado: str
    creado_en: datetime
    # Spec `prestamos-confirmacion-mutua` (T3): campos aditivos.
    # `estado_confirmacion` es una property Python del modelo (no una
    # columna) — Pydantic la lee igual que cualquier otro atributo vía
    # `orm_mode`.
    confirmado_prestamista: Optional[bool] = None
    confirmado_deudor: Optional[bool] = None
    estado_confirmacion: str

    class Config:
        orm_mode = True


@prestamos_router.post(
    "/{casa_id}/prestamos",
    response_model=PrestamoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_prestamo_endpoint(
    casa_id: UUID,
    payload: PrestamoCreate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return crear_prestamo(
            casa_id,
            payload.prestamista_id,
            payload.deudor_id,
            payload.importe,
            payload.moneda or "ARS",
            payload.fecha,
            actor,
            descripcion=payload.descripcion,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@prestamos_router.get("/{casa_id}/prestamos", response_model=list[PrestamoOut])
def listar_prestamos_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        return listar_prestamos(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@prestamos_router.patch("/{casa_id}/prestamos/{prestamo_id}", response_model=PrestamoOut)
def actualizar_estado_prestamo_endpoint(
    casa_id: UUID,
    prestamo_id: UUID,
    payload: PrestamoEstadoUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return actualizar_estado_prestamo(casa_id, prestamo_id, payload.estado, actor)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@prestamos_router.patch(
    "/{casa_id}/prestamos/{prestamo_id}/confirmacion", response_model=PrestamoOut
)
def confirmar_prestamo_endpoint(
    casa_id: UUID,
    prestamo_id: UUID,
    payload: PrestamoConfirmacionUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    """Confirma o rechaza el rol de `actor` en este préstamo (spec
    `prestamos-confirmacion-mutua`, T3). Ruta propia, separada del PATCH
    de estado de arriba — modelos de permiso distintos (ver Design
    Rationale de T3): cambiar pagado/pendiente es abierto a cualquier
    miembro activo; confirmar/rechazar exige ser específicamente una de
    las dos partes de ESTE préstamo."""
    try:
        return confirmar_prestamo(casa_id, prestamo_id, actor, payload.confirma)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
