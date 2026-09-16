"""Rutas HTTP de ItemMantenimiento — adaptador delgado sobre T2
(`mantenimiento_service`).

Ninguna regla de negocio vive aquí: cada handler valida forma (vía
Pydantic), delega en el servicio correspondiente y traduce las
excepciones de dominio a códigos HTTP, siguiendo el mismo patrón que
`src/api/routes/tarjetas.py`.

Router propio (no agregado a otro archivo) — mismo criterio que separó
`tarjetas.py`/`prestamos.py`/`tareas.py` entre sí: un recurso HTTP por
módulo, todos bajo el prefijo compartido `/casas`.
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from src.api.dependencies import resolver_actor_en_casa
from src.services.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from src.services.mantenimiento_service import (
    actualizar_material,
    agregar_material,
    completar_item,
    crear_item,
    listar_items,
)

mantenimiento_router = APIRouter(prefix="/casas", tags=["mantenimiento"])


class MaterialCreate(BaseModel):
    nombre: str
    cantidad: int = 1


class ItemMantenimientoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_estimada: Optional[date] = None
    recurrente: bool = False
    periodicidad: Optional[str] = None
    materiales: Optional[List[MaterialCreate]] = None
    # Spec `mantenimiento-autos`, REQ-002: opcional — asocia el ítem a un
    # auto puntual en vez de a la casa.
    auto_id: Optional[UUID] = None


class ItemMantenimientoEstadoUpdate(BaseModel):
    estado: str


class MaterialEstadoUpdate(BaseModel):
    conseguido: bool


class MaterialOut(BaseModel):
    id: UUID
    item_mantenimiento_id: UUID
    nombre: str
    cantidad: int
    conseguido: bool

    class Config:
        orm_mode = True


class ItemMantenimientoOut(BaseModel):
    id: UUID
    casa_id: UUID
    nombre: str
    descripcion: Optional[str] = None
    fecha_estimada: Optional[date] = None
    recurrente: bool
    periodicidad: Optional[str] = None
    estado: str
    creado_en: datetime
    materiales: List[MaterialOut] = []
    # Spec `mantenimiento-autos`, REQ-002/REQ-003 (aditivo).
    auto_id: Optional[UUID] = None

    class Config:
        orm_mode = True


class ItemMantenimientoAlertaOut(BaseModel):
    id: UUID
    nombre: str
    fecha_estimada: date
    dias_para_vencimiento: int
    vencido: bool
    # Spec `mantenimiento-autos`, REQ-004 (aditivo): `None` para un ítem
    # de la casa; poblados cuando el ítem pertenece a un auto, para que
    # el frontend arme el texto de la alerta mencionándolo.
    auto_id: Optional[UUID] = None
    auto_nombre: Optional[str] = None

    class Config:
        orm_mode = True


@mantenimiento_router.post(
    "/{casa_id}/mantenimiento",
    response_model=ItemMantenimientoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_item_endpoint(
    casa_id: UUID,
    payload: ItemMantenimientoCreate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return crear_item(
            casa_id,
            payload.nombre,
            payload.descripcion,
            payload.fecha_estimada,
            payload.recurrente,
            payload.periodicidad,
            actor,
            materiales=[m.dict() for m in payload.materiales] if payload.materiales else None,
            auto_id=payload.auto_id,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@mantenimiento_router.get("/{casa_id}/mantenimiento", response_model=List[ItemMantenimientoOut])
def listar_items_endpoint(
    casa_id: UUID,
    actor: UUID = Depends(resolver_actor_en_casa),
    auto_id: Optional[UUID] = Query(default=None, alias="autoId"),
):
    try:
        return listar_items(casa_id, auto_id=auto_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@mantenimiento_router.patch(
    "/{casa_id}/mantenimiento/{item_id}", response_model=ItemMantenimientoOut
)
def actualizar_estado_item_endpoint(
    casa_id: UUID,
    item_id: UUID,
    payload: ItemMantenimientoEstadoUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    if payload.estado != "completado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta spec solo soporta la transición de estado a 'completado'.",
        )
    try:
        return completar_item(casa_id, item_id, actor)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@mantenimiento_router.post(
    "/{casa_id}/mantenimiento/{item_id}/materiales",
    response_model=MaterialOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_material_endpoint(
    casa_id: UUID,
    item_id: UUID,
    payload: MaterialCreate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return agregar_material(casa_id, item_id, payload.nombre, payload.cantidad, actor)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@mantenimiento_router.patch(
    "/{casa_id}/mantenimiento/{item_id}/materiales/{material_id}", response_model=MaterialOut
)
def actualizar_material_endpoint(
    casa_id: UUID,
    item_id: UUID,
    material_id: UUID,
    payload: MaterialEstadoUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    try:
        return actualizar_material(casa_id, item_id, material_id, payload.conseguido, actor)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
