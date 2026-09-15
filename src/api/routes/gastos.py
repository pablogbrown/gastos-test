"""Rutas HTTP de Categorías, Gastos y Balance — adaptadores delgados
sobre T2 (`categoria_service`, `gasto_service`, `balance_service`).

Ninguna regla de negocio vive aquí: cada handler valida forma (vía
Pydantic), delega en el servicio correspondiente y traduce las
excepciones de dominio a códigos HTTP, siguiendo el mismo patrón que
`src/api/routes/casas.py` (`casas-miembros`).

Los esquemas Pydantic de este router viven en este mismo archivo (en vez
de `src/api/schemas.py`) porque el scope de esta spec, fijado por
`run-plan.json`, solo declara `src/api/routes/gastos.py`.

Nota de diseño (pagado_por): el contrato HTTP documentado en
`00-overview.md` no incluye un campo `pagadoPor` explícito en el body de
`POST .../gastos` — solo `descripcion, importe, fecha, categoriaId,
participantes?`. Se interpreta que, por defecto, quien registra el gasto
(`actor`, resuelto del JWT — spec `usuarios-auth`) es también quien lo
pagó; `pagado_por` queda como campo opcional para permitir que un
Administrador registre un gasto en nombre de otro miembro sin romper el
contrato documentado.

Nota de diseño (spec `usuarios-auth`): el `actor` ya no llega vía el
header placeholder `X-Usuario-Id` — se resuelve desde un JWT real vía
`resolver_actor_en_casa` (`src/api/dependencies.py`), que además valida
membresía activa (REQ-005) antes de delegar en los servicios de T2, que
no cambian.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.dependencies import resolver_actor_en_casa
from src.services.balance_service import calcular_balance, sugerir_transferencias
from src.services.categoria_service import crear_categoria, listar_categorias
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.gasto_service import listar_gastos, registrar_gasto

gastos_router = APIRouter(prefix="/casas", tags=["gastos"])


class CategoriaCreate(BaseModel):
    nombre: str


class CategoriaOut(BaseModel):
    id: UUID
    casa_id: UUID
    nombre: str

    class Config:
        orm_mode = True


class GastoCreate(BaseModel):
    descripcion: str
    importe: Decimal
    fecha: date
    # Optional a nivel de esquema (en vez de requerido) para que un
    # payload sin `categoria_id` llegue al servicio y sea rechazado con
    # 400 vía `ValidationError` (TC-002), en vez de un 422 genérico de
    # validación de Pydantic.
    categoria_id: Optional[UUID] = None
    pagado_por: Optional[UUID] = None
    participantes: Optional[List[UUID]] = None
    # Spec `gastos-en-cuotas`: idem — Optional a nivel de esquema para
    # que un valor inválido (0/negativo) llegue al servicio y sea
    # rechazado con 400 vía `ValidationError` (TC-005), no un 422.
    cuotas: Optional[int] = None
    # Spec `gastos-multi-moneda`: idem — Optional a nivel de esquema para
    # que un valor inválido (ej. "EUR") llegue al servicio y sea
    # rechazado con 400 vía `ValidationError` (TC-008), no un 422
    # genérico de Pydantic. Ausente -> "ARS" (REQ-001).
    moneda: Optional[str] = None


class ParticipanteOut(BaseModel):
    miembro_id: UUID
    monto_correspondiente: Decimal

    class Config:
        orm_mode = True


class GastoOut(BaseModel):
    id: UUID
    casa_id: UUID
    descripcion: str
    importe: Decimal
    fecha: date
    pagado_por: UUID
    categoria_id: UUID
    participantes: List[ParticipanteOut] = Field(default_factory=list)
    # Spec `gastos-en-cuotas`: `None` para un gasto sin cuotas — aditivo.
    cuota_grupo_id: Optional[UUID] = None
    cuota_numero: Optional[int] = None
    cuota_total: Optional[int] = None
    # Spec `gastos-suscripcion-mensual`: `None` para un gasto normal o en
    # cuotas — aditivo, independiente de los campos de cuotas de arriba.
    suscripcion_id: Optional[UUID] = None
    # Spec `gastos-multi-moneda`: siempre presente ("ARS" o "USD") — a
    # diferencia de `GastoCreate.moneda`, acá es requerido porque
    # `gasto_service.registrar_gasto` siempre persiste un valor válido.
    moneda: str

    class Config:
        orm_mode = True


class BalancePorMiembroOut(BaseModel):
    miembro_id: UUID
    nombre: str
    pago: Decimal
    correspondia: Decimal
    balance: Decimal
    # Spec `gastos-multi-moneda`, REQ-002: la moneda de esta fila —
    # `calcular_balance` ahora agrupa por (miembro, moneda).
    moneda: str

    class Config:
        orm_mode = True


class TransferenciaOut(BaseModel):
    deudor_id: UUID
    acreedor_id: UUID
    monto: Decimal
    # Spec `gastos-multi-moneda`, REQ-003: la moneda del grupo dentro del
    # que se sugirió esta transferencia — nunca mezclada entre monedas.
    moneda: str

    class Config:
        orm_mode = True


class BalanceResponse(BaseModel):
    balances: List[BalancePorMiembroOut]
    transferencias: List[TransferenciaOut]


@gastos_router.post(
    "/{casa_id}/categorias", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED
)
def crear_categoria_endpoint(
    casa_id: UUID, payload: CategoriaCreate, actor: UUID = Depends(resolver_actor_en_casa)
):
    try:
        return crear_categoria(casa_id, payload.nombre, actor)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@gastos_router.get("/{casa_id}/categorias", response_model=List[CategoriaOut])
def listar_categorias_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        return listar_categorias(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@gastos_router.post("/{casa_id}/gastos", response_model=GastoOut, status_code=status.HTTP_201_CREATED)
def registrar_gasto_endpoint(
    casa_id: UUID, payload: GastoCreate, actor: UUID = Depends(resolver_actor_en_casa)
):
    try:
        return registrar_gasto(
            casa_id,
            payload.descripcion,
            payload.importe,
            payload.fecha,
            payload.categoria_id,
            payload.pagado_por or actor,
            actor,
            participantes=payload.participantes,
            cuotas=payload.cuotas,
            moneda=payload.moneda or "ARS",
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@gastos_router.get("/{casa_id}/gastos", response_model=List[GastoOut])
def listar_gastos_endpoint(casa_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)):
    try:
        return listar_gastos(casa_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@gastos_router.get("/{casa_id}/balance", response_model=BalanceResponse)
def obtener_balance_endpoint(
    casa_id: UUID, mes: Optional[str] = None, actor: UUID = Depends(resolver_actor_en_casa)
):
    try:
        balances = calcular_balance(casa_id, mes)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    transferencias = sugerir_transferencias(balances)
    return BalanceResponse(balances=balances, transferencias=transferencias)
