"""Rutas HTTP de la Tienda de accesorios — adaptadores delgados sobre
`tienda_service`.

Mismo patrón que `avatares.py`: ninguna regla de negocio vive acá; el
actor autenticado se resuelve vía `resolver_actor_en_casa`.

Desviación deliberada del contrato literal de `spec.md` (Judgment, ver
`build-results.md`), mismo criterio y misma razón ya establecidos por
`avatares.py`: spec.md describe estas rutas como `/accesorios?miembro_id=...`
y `/miembros/{miembro_id}/...`, sin `casa_id`. Esta spec las anida bajo
`/casas/{casa_id}/miembros/{miembro_id}/accesorios/...` — porque
`resolver_actor_en_casa` exige un `casa_id` de la URL para resolver el
actor, y el proxy de Vite solo reenvía `/casas`/`/auth`. El catálogo
filtrado (antes `GET /accesorios?miembro_id=...`) pasa a
`GET .../accesorios/catalogo` para no colisionar con el inventario (antes
`GET /miembros/{miembro_id}/accesorios`, ahora la misma ruta bare
`GET .../accesorios`).

Las 2 rutas GET son legibles por cualquier miembro activo de la casa
(mismo criterio de apertura ya establecido para Ranking/Historial/
Avatares — nada en esta app es privado por miembro). El POST de compra,
el PUT de equipar y el DELETE de desequipar son self-service: solo el
propio miembro puede gastar SUS créditos y cambiar SU avatar (ninguno de
REQ-002/REQ-003 menciona un override de Administrador, mismo criterio ya
aplicado al PUT de selección de avatar en `avatares.py`).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import resolver_actor_en_casa
from src.api.schemas import AccesorioAvatarOut, AccesorioEquiparUpdate
from src.services.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from src.services.tienda_service import (
    comprar_accesorio,
    desequipar_slot,
    equipar_accesorio,
    listar_catalogo_accesorios,
    listar_inventario,
)

tienda_router = APIRouter(tags=["tienda"])


def _exigir_self_service(actor: UUID, miembro_id: UUID) -> None:
    if actor != miembro_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el propio miembro puede operar sobre su tienda de accesorios.",
        )


def _accesorio_del_inventario_o_404(miembro_id: UUID, accesorio_id: UUID):
    """`comprar_accesorio`/`equipar_accesorio` devuelven la fila del join
    (`MiembroAccesorioComprado`/`MiembroAccesorioEquipado`, ver
    `interfaces_produced` de T2/T3), no el `AccesorioAvatar` que esta
    ruta expone (`response_model=AccesorioAvatarOut`) — este helper
    resuelve esa traducción una sola vez para ambos endpoints."""
    for accesorio in listar_inventario(miembro_id):
        if accesorio.id == accesorio_id:
            return accesorio
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Accesorio no encontrado en el inventario.")


@tienda_router.get(
    "/casas/{casa_id}/miembros/{miembro_id}/accesorios/catalogo",
    response_model=list[AccesorioAvatarOut],
)
def listar_catalogo_accesorios_endpoint(
    casa_id: UUID, miembro_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)
):
    return listar_catalogo_accesorios(miembro_id)


@tienda_router.get(
    "/casas/{casa_id}/miembros/{miembro_id}/accesorios",
    response_model=list[AccesorioAvatarOut],
)
def listar_inventario_endpoint(
    casa_id: UUID, miembro_id: UUID, actor: UUID = Depends(resolver_actor_en_casa)
):
    return listar_inventario(miembro_id)


@tienda_router.post(
    "/casas/{casa_id}/miembros/{miembro_id}/accesorios/{accesorio_id}/comprar",
    response_model=AccesorioAvatarOut,
)
def comprar_accesorio_endpoint(
    casa_id: UUID,
    miembro_id: UUID,
    accesorio_id: UUID,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    _exigir_self_service(actor, miembro_id)
    try:
        comprar_accesorio(miembro_id, accesorio_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValidationError as exc:
        # 402 (no 400): spec.md, Contracts — saldo insuficiente es la
        # única condición de compra que esta ruta mapea a 402, no al 400
        # que el resto de `ValidationError` del proyecto usa (autos.py,
        # gastos.py, etc.) — ver Judgment de este build.
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(exc)) from exc

    return _accesorio_del_inventario_o_404(miembro_id, accesorio_id)


@tienda_router.put(
    "/casas/{casa_id}/miembros/{miembro_id}/accesorios/equipar",
    response_model=AccesorioAvatarOut,
)
def equipar_accesorio_endpoint(
    casa_id: UUID,
    miembro_id: UUID,
    payload: AccesorioEquiparUpdate,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    _exigir_self_service(actor, miembro_id)
    try:
        equipar_accesorio(miembro_id, payload.accesorio_id)
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return _accesorio_del_inventario_o_404(miembro_id, payload.accesorio_id)


@tienda_router.delete(
    "/casas/{casa_id}/miembros/{miembro_id}/accesorios/{slot}/equipado",
    status_code=status.HTTP_204_NO_CONTENT,
)
def desequipar_slot_endpoint(
    casa_id: UUID,
    miembro_id: UUID,
    slot: str,
    actor: UUID = Depends(resolver_actor_en_casa),
):
    _exigir_self_service(actor, miembro_id)
    desequipar_slot(miembro_id, slot)
