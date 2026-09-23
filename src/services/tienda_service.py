"""Servicio de Tienda de accesorios: catálogo, compra (gasta créditos) y
equipar/desequipar por slot (spec `tienda-accesorios`, REQ-001 a REQ-004).

Depende de `avatar_service.obtener_balance_creditos`/
`obtener_avatar_seleccionado` (spec `avatares-economia`, ya construida y
estable) — este servicio las CONSUME, nunca las reimplementa (spec.md,
Constraints). El descuento de créditos (T2) reusa el mismo ledger
`CreditoTransaccion` de `avatares-economia` (`motivo="compra_accesorio"`)
— esta spec no crea un segundo mecanismo de contabilidad.

Cada función pública abre y cierra su propia sesión (mismo patrón que
`avatar_service.py`) — ninguna toma `session` como parámetro, porque
ninguna se llama desde dentro de la transacción de otro servicio
([SERVP-01] no aplica acá).
"""
import uuid
from datetime import date
from typing import List
from uuid import UUID

from sqlalchemy import or_

from src.db.base import get_session
from src.db.models.accesorio_avatar import AccesorioAvatar
from src.db.models.credito_transaccion import CreditoTransaccion
from src.db.models.miembro_accesorio_comprado import MiembroAccesorioComprado
from src.db.models.miembro_accesorio_equipado import MiembroAccesorioEquipado
from src.services.avatar_service import obtener_avatar_seleccionado, obtener_balance_creditos
from src.services.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError


def listar_catalogo_accesorios(miembro_id: UUID) -> List[AccesorioAvatar]:
    """Catálogo de compra de accesorios para `miembro_id` (REQ-001):
    filtrado por la especie de SU avatar actualmente seleccionado
    (`avatar_service.obtener_avatar_seleccionado`) — un accesorio
    compatible solo con "gato" no aparece para quien tiene un perro
    seleccionado; sin avatar seleccionado, se muestra el catálogo
    completo sin filtrar por especie. En ambos casos, excluye accesorios
    fuera de su ventana de disponibilidad (REQ-004) — el catálogo de
    COMPRA nunca incluye un ítem vencido, ya sea que el miembro lo tenga
    o no (uno ya comprado se rechaza igual por REQ-002 si intentara
    comprarlo de nuevo, y sigue visible/equipable vía `listar_inventario`,
    T2, sin importar la ventana — ver ese servicio)."""
    hoy = date.today()
    session = get_session()
    try:
        query = session.query(AccesorioAvatar).filter(
            or_(AccesorioAvatar.disponible_desde.is_(None), AccesorioAvatar.disponible_desde <= hoy),
            or_(AccesorioAvatar.disponible_hasta.is_(None), AccesorioAvatar.disponible_hasta >= hoy),
        )
        avatar_actual = obtener_avatar_seleccionado(miembro_id)
        if avatar_actual is not None:
            query = query.filter(
                or_(
                    AccesorioAvatar.especie_compatible == avatar_actual.especie,
                    AccesorioAvatar.especie_compatible == "ambos",
                )
            )
        return query.all()
    finally:
        session.close()


def listar_inventario(miembro_id: UUID) -> List[AccesorioAvatar]:
    """Accesorios que `miembro_id` ya compró (REQ-002), SIN aplicar el
    filtro de ventana de disponibilidad de `listar_catalogo_accesorios`
    (REQ-004) — un accesorio ya comprado se conserva visible/equipable en
    el inventario aunque su ventana ya haya cerrado (TC-010)."""
    session = get_session()
    try:
        return (
            session.query(AccesorioAvatar)
            .join(
                MiembroAccesorioComprado,
                MiembroAccesorioComprado.accesorio_id == AccesorioAvatar.id,
            )
            .filter(MiembroAccesorioComprado.miembro_id == miembro_id)
            .all()
        )
    finally:
        session.close()


def _casa_id_del_miembro(session, miembro_id: UUID):
    """`CreditoTransaccion.casa_id` es `NOT NULL` (spec `avatares-economia`)
    — se resuelve acá desde `Miembro.casa_id`, nunca duplicado ni pasado
    por el caller, mismo criterio que `avatar_service.otorgar_creditos`
    recibe `casa_id` de su propio caller (`tarea_service`, que ya conoce
    la casa de la tarea)."""
    from src.db.models.miembro import Miembro

    miembro = session.get(Miembro, miembro_id)
    if miembro is None:
        raise NotFoundError(f"El miembro {miembro_id} no existe.")
    return miembro.casa_id


def comprar_accesorio(miembro_id: UUID, accesorio_id: UUID) -> MiembroAccesorioComprado:
    """Compra un accesorio para `miembro_id` (REQ-002): rechaza
    (`NotFoundError`, 404) si el accesorio no existe; rechaza
    (`ConflictError`, 409) si ya está en el inventario del miembro (evita
    descuento doble, TC-005); rechaza (`ValidationError`, mapeado a 402 en
    la ruta — spec.md Contracts) si el saldo de créditos
    (`avatar_service.obtener_balance_creditos`) es menor al precio del
    accesorio (TC-004). Si pasa, crea una `CreditoTransaccion` negativa
    por el precio (`motivo="compra_accesorio"`, reusando el ledger de
    `avatares-economia`) y la fila de compra, ambas en la misma
    transacción (atómico: ambas o ninguna)."""
    session = get_session()
    try:
        accesorio = session.get(AccesorioAvatar, accesorio_id)
        if accesorio is None:
            raise NotFoundError(f"El accesorio {accesorio_id} no existe.")

        ya_comprado = session.get(MiembroAccesorioComprado, (miembro_id, accesorio_id))
        if ya_comprado is not None:
            raise ConflictError(f"El miembro {miembro_id} ya compró el accesorio {accesorio_id}.")

        saldo = obtener_balance_creditos(miembro_id)
        if saldo < accesorio.precio_creditos:
            raise ValidationError(
                f"Saldo insuficiente: {saldo} créditos disponibles, se requieren {accesorio.precio_creditos}."
            )

        transaccion = CreditoTransaccion(
            id=uuid.uuid4(),
            casa_id=_casa_id_del_miembro(session, miembro_id),
            miembro_id=miembro_id,
            cantidad=-accesorio.precio_creditos,
            motivo="compra_accesorio",
        )
        session.add(transaccion)

        compra = MiembroAccesorioComprado(miembro_id=miembro_id, accesorio_id=accesorio_id)
        session.add(compra)

        session.commit()
        session.refresh(compra)
        return compra
    finally:
        session.close()


def equipar_accesorio(miembro_id: UUID, accesorio_id: UUID) -> MiembroAccesorioEquipado:
    """Equipa un accesorio COMPRADO y compatible con la especie del
    avatar actual de `miembro_id` (REQ-003): rechaza (`PermissionDeniedError`,
    403) si el accesorio no está en `listar_inventario` (TC-007) o si no
    es compatible con la especie del avatar actualmente seleccionado. Si
    pasa, upsert de `MiembroAccesorioEquipado` sobre `(miembro_id, slot)`
    — la clave primaria compuesta es lo que garantiza el reemplazo, nunca
    dos filas activas para el mismo slot (TC-008)."""
    inventario = {accesorio.id: accesorio for accesorio in listar_inventario(miembro_id)}
    accesorio = inventario.get(accesorio_id)
    if accesorio is None:
        raise PermissionDeniedError(
            f"El accesorio {accesorio_id} no está en el inventario del miembro {miembro_id}."
        )

    avatar_actual = obtener_avatar_seleccionado(miembro_id)
    if (
        avatar_actual is not None
        and accesorio.especie_compatible != "ambos"
        and accesorio.especie_compatible != avatar_actual.especie
    ):
        raise PermissionDeniedError(
            f"El accesorio {accesorio_id} no es compatible con la especie del avatar actual."
        )

    session = get_session()
    try:
        equipado = session.get(MiembroAccesorioEquipado, (miembro_id, accesorio.slot))
        if equipado is None:
            equipado = MiembroAccesorioEquipado(
                miembro_id=miembro_id, slot=accesorio.slot, accesorio_id=accesorio_id
            )
            session.add(equipado)
        else:
            equipado.accesorio_id = accesorio_id
        session.commit()
        session.refresh(equipado)
        return equipado
    finally:
        session.close()


def desequipar_slot(miembro_id: UUID, slot: str) -> None:
    """Desequipa el `slot` de `miembro_id` (REQ-003) — no-op si no hay
    nada equipado en ese slot."""
    session = get_session()
    try:
        equipado = session.get(MiembroAccesorioEquipado, (miembro_id, slot))
        if equipado is not None:
            session.delete(equipado)
            session.commit()
    finally:
        session.close()


def listar_equipados(miembro_id: UUID) -> List[MiembroAccesorioEquipado]:
    """Accesorios actualmente equipados por `miembro_id`, uno por slot
    como máximo (REQ-003) — usado por la ruta de lectura del estado de
    equipado, mismo criterio de exposición ya establecido para el resto
    del estado de avatar (nada es privado por miembro en esta app)."""
    session = get_session()
    try:
        return (
            session.query(MiembroAccesorioEquipado)
            .filter(MiembroAccesorioEquipado.miembro_id == miembro_id)
            .all()
        )
    finally:
        session.close()
