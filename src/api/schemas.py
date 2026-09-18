"""Esquemas Pydantic de request/response para las rutas de casas/miembros
y de tareas/puntos."""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CasaCreate(BaseModel):
    nombre: str


class MiembroCreate(BaseModel):
    """Spec `usuarios-auth` (REQ-004): `email` reemplaza el id de miembro
    arbitrario que el cliente podía enviar antes — el nuevo Miembro se
    vincula al Usuario ya registrado con ese email (404 si no existe)."""

    nombre: str
    identificacion: str
    email: str


class MiembroActivoUpdate(BaseModel):
    activo: bool


class MiembroOut(BaseModel):
    id: UUID
    usuario_id: Optional[UUID] = None
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
    # Spec `gamificacion-puntos`, REQ-005 — sin alias (`CasaOut` no sigue
    # el criterio de `DashboardOut`, [API-01]: cada campo de este schema
    # ya era snake_case desde antes).
    meta_puntos_mensual: Optional[int] = None

    class Config:
        orm_mode = True


class MetaPuntosUpdate(BaseModel):
    """Spec `gamificacion-puntos`, REQ-005 — `meta=None` desactiva la
    meta (vuelve a no mostrarse en Inicio)."""

    meta: Optional[int] = None


class TareaCreate(BaseModel):
    """Body de creación de Tarea (contrato de `00-overview.md`: `puntos` es
    Optional a nivel de esquema a propósito, para que su ausencia dispare
    la validación de negocio de `crear_tarea` — 400, no 422 — igual que un
    nombre vacío."""

    nombre: str
    puntos: Optional[int] = None
    descripcion: Optional[str] = None
    responsable_id: Optional[UUID] = Field(default=None, alias="responsableId")
    fecha_prevista: Optional[date] = Field(default=None, alias="fechaPrevista")
    recurrente: bool = False
    frecuencia: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class TareaEstadoUpdate(BaseModel):
    estado: str


class TareaOut(BaseModel):
    id: UUID
    casa_id: UUID
    nombre: str
    descripcion: Optional[str] = None
    puntos: int
    responsable_id: Optional[UUID] = Field(default=None, alias="responsableId")
    fecha_prevista: Optional[date] = Field(default=None, alias="fechaPrevista")
    estado: str
    recurrente: bool
    frecuencia: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class HistorialTareaOut(BaseModel):
    id: UUID
    tarea_id: UUID
    miembro_id: UUID
    completada_en: datetime
    puntos_obtenidos: int

    class Config:
        orm_mode = True


class LogroObtenidoOut(BaseModel):
    """Spec `gamificacion-puntos`, REQ-004 — sin alias: mismo criterio que
    `HistorialTareaOut`/`TarjetaAlertaOut`, snake_case plano."""

    id: UUID
    casa_id: UUID
    miembro_id: UUID
    logro_id: str
    obtenido_en: datetime

    class Config:
        orm_mode = True


class RankingEntryOut(BaseModel):
    miembro_id: UUID = Field(alias="miembroId")
    puntos: int
    # Spec `gamificacion-puntos`, REQ-001/REQ-002: nivel (total histórico)
    # y racha (días consecutivos) de cada miembro — [API-01]'s exception
    # ya establecida para este schema (`RankingEntryOut.miembro_id ->
    # miembroId`) no se extiende: `nivel`/`racha` van sin alias, iguales a
    # `puntos`.
    nivel: str
    racha: int

    class Config:
        allow_population_by_field_name = True
