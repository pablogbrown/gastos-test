"""Esquemas Pydantic de request/response para las rutas de casas/miembros."""
from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class CasaCreate(BaseModel):
    nombre: str


class MiembroCreate(BaseModel):
    nombre: str
    identificacion: str


class MiembroActivoUpdate(BaseModel):
    activo: bool


class MiembroOut(BaseModel):
    id: UUID
    casa_id: UUID
    nombre: str
    identificacion: str
    rol: str
    activo: bool

    class Config:
        orm_mode = True


class CasaOut(BaseModel):
    id: UUID
    nombre: str
    creado_en: datetime
    miembros: List[MiembroOut] = Field(default_factory=list)

    class Config:
        orm_mode = True
