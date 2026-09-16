"""Servicio de ItemMantenimiento: alta con materiales, materiales
individuales, completar con generación de recurrencia y cálculo de
alerta de vencimiento cercano (spec `mantenimiento-casa`).

Reutiliza el guard `requiere_membresia_activa` de `miembro_service` (igual
que `gasto_service`/`tarea_service`/`tarjeta_service`): cualquier miembro
activo de la casa puede operar, sin guard de rol adicional.

El gate de "recurrente exige periodicidad Y fecha estimada" y el de "no
se puede completar una instancia recurrente antes de su propia fecha"
replican el criterio recién corregido en `tarea_service.crear_tarea`/
`completar_tarea` — código propio, deliberadamente NO compartido (mismo
criterio de un-servicio-por-responsabilidad ya usado para `_sumar_meses`/
`_rango_mes`). `_DIAS_POR_PERIODICIDAD` usa días fijos, no aritmética de
mes calendario — más simple que `tarea_service`, deliberado (ver
`00-overview.md`).

`obtener_items_con_alerta` vive acá (no en `dashboard_service`), mismo
criterio que `tarjeta_service.obtener_tarjetas_con_alerta`: la lógica de
negocio de "qué es una alerta" pertenece al dominio del ítem, el
dashboard solo la consume.
"""
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import selectinload

from src.db.base import get_session
from src.db.models.auto import Auto
from src.db.models.casa import Casa
from src.db.models.mantenimiento import ItemMantenimiento, MaterialMantenimiento
from src.services.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import requiere_membresia_activa

PERIODICIDADES_VALIDAS = {"semanal", "mensual", "trimestral", "semestral", "anual"}

_DIAS_POR_PERIODICIDAD = {
    "semanal": 7,
    "mensual": 30,
    "trimestral": 90,
    "semestral": 180,
    "anual": 365,
}

UMBRAL_ALERTA_DIAS = 7


@dataclass
class ItemMantenimientoAlerta:
    """Un ítem de mantenimiento pendiente cuya `fecha_estimada` está a
    `UMBRAL_ALERTA_DIAS` días o menos (o ya venció) — lo que
    `dashboard_service` consume para armar el banner de Inicio
    (REQ-005).

    `auto_id`/`auto_nombre` (spec `mantenimiento-autos`, REQ-004):
    `None` para un ítem de la casa; poblados cuando el ítem pertenece a
    un auto, para que el frontend arme el texto de la alerta
    mencionándolo — sin una sección separada, mismo banner combinado
    (decisión explícita del usuario, ver `00-overview.md`'s Tradeoffs)."""

    id: UUID
    nombre: str
    fecha_estimada: date
    dias_para_vencimiento: int
    vencido: bool
    auto_id: Optional[UUID] = None
    auto_nombre: Optional[str] = None


def _obtener_item_o_none(session, casa_id: UUID, item_id: UUID):
    return (
        session.query(ItemMantenimiento)
        .filter(ItemMantenimiento.casa_id == casa_id, ItemMantenimiento.id == item_id)
        .one_or_none()
    )


def _obtener_material_o_none(session, item_id: UUID, material_id: UUID):
    return (
        session.query(MaterialMantenimiento)
        .filter(
            MaterialMantenimiento.item_mantenimiento_id == item_id,
            MaterialMantenimiento.id == material_id,
        )
        .one_or_none()
    )


def crear_item(
    casa_id: UUID,
    nombre: str,
    descripcion: Optional[str],
    fecha_estimada: Optional[date],
    recurrente: bool,
    periodicidad: Optional[str],
    actor: UUID,
    materiales: Optional[List[dict]] = None,
    auto_id: Optional[UUID] = None,
) -> ItemMantenimiento:
    """Crea un ItemMantenimiento en estado "pendiente" (REQ-001, TC-001).

    Si `recurrente`, exige `periodicidad` en `PERIODICIDADES_VALIDAS` Y
    `fecha_estimada` no `None` — sin una fecha de anclaje no hay forma de
    impedir que se complete más seguido que su periodicidad (mismo
    criterio recién corregido en `tarea_service.crear_tarea`, TC-002).
    `materiales` (opcional): lista de `{nombre, cantidad}` — crea una fila
    `MaterialMantenimiento` por cada uno, `conseguido=False` (TC-003).

    `auto_id` (spec `mantenimiento-autos`, REQ-002): opcional — si se
    provee, debe corresponder a un `Auto` que exista en `casa_id`
    (`NotFoundError` si no — cubre también el caso de un auto de otra
    casa, TC-005, ya que la búsqueda está scopeada por `casa_id`).
    """
    if not nombre or not str(nombre).strip():
        raise ValidationError("El nombre del ítem de mantenimiento no puede estar vacío.")
    if recurrente and periodicidad not in PERIODICIDADES_VALIDAS:
        raise ValidationError(
            "Un ítem recurrente debe indicar una periodicidad válida "
            f"({', '.join(sorted(PERIODICIDADES_VALIDAS))})."
        )
    if recurrente and fecha_estimada is None:
        raise ValidationError("Un ítem recurrente debe indicar una fecha estimada.")

    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        if auto_id is not None:
            auto = (
                session.query(Auto)
                .filter(Auto.id == auto_id, Auto.casa_id == casa_id)
                .one_or_none()
            )
            if auto is None:
                raise NotFoundError(f"El auto {auto_id} no existe en la casa {casa_id}.")

        item = ItemMantenimiento(
            id=uuid.uuid4(),
            casa_id=casa_id,
            nombre=nombre.strip(),
            descripcion=descripcion,
            fecha_estimada=fecha_estimada,
            recurrente=bool(recurrente),
            periodicidad=periodicidad if recurrente else None,
            estado="pendiente",
            auto_id=auto_id,
        )
        for material in materiales or []:
            item.materiales.append(
                MaterialMantenimiento(
                    id=uuid.uuid4(),
                    nombre=material["nombre"],
                    cantidad=material.get("cantidad", 1),
                    conseguido=False,
                )
            )

        session.add(item)
        session.commit()
        session.refresh(item)
        # Fuerza la carga de `materiales` mientras la sesión sigue abierta
        # — expirada tras el commit (`expire_on_commit`, default de
        # `SessionLocal`), se perdería con un `DetachedInstanceError` si el
        # caller la accede después de que este `finally` cierre la sesión.
        list(item.materiales)
        return item
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def agregar_material(
    casa_id: UUID, item_id: UUID, nombre: str, cantidad: int, actor: UUID
) -> MaterialMantenimiento:
    """Agrega un material a un ítem ya existente (REQ-003)."""
    if not nombre or not str(nombre).strip():
        raise ValidationError("El nombre del material no puede estar vacío.")

    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        item = _obtener_item_o_none(session, casa_id, item_id)
        if item is None:
            raise NotFoundError(f"El ítem de mantenimiento {item_id} no existe en la casa {casa_id}.")

        material = MaterialMantenimiento(
            id=uuid.uuid4(),
            item_mantenimiento_id=item.id,
            nombre=nombre.strip(),
            cantidad=cantidad if cantidad is not None else 1,
            conseguido=False,
        )
        session.add(material)
        session.commit()
        session.refresh(material)
        return material
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def actualizar_material(
    casa_id: UUID, item_id: UUID, material_id: UUID, conseguido: bool, actor: UUID
) -> MaterialMantenimiento:
    """Marca un material como conseguido/pendiente (REQ-003, TC-004)."""
    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        item = _obtener_item_o_none(session, casa_id, item_id)
        if item is None:
            raise NotFoundError(f"El ítem de mantenimiento {item_id} no existe en la casa {casa_id}.")

        material = _obtener_material_o_none(session, item.id, material_id)
        if material is None:
            raise NotFoundError(f"El material {material_id} no existe en el ítem {item_id}.")

        material.conseguido = bool(conseguido)
        session.commit()
        session.refresh(material)
        return material
    except (PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def listar_items(casa_id: UUID, auto_id: Optional[UUID] = None) -> List[ItemMantenimiento]:
    """Lista los ítems de mantenimiento de una casa (spec
    `mantenimiento-autos`, REQ-003, TC-003).

    Sin `auto_id`: solo los ítems de la casa (`auto_id IS NULL`) — cambio
    deliberado de comportamiento respecto a `mantenimiento-casa` (donde
    la columna no existía y todo ítem era implícitamente de la casa):
    ahora que `auto_id` existe, "sin auto_id" debe significar "solo los
    de la casa", no "todos sin importar auto_id", para que la pantalla
    "Mantenimiento" siga mostrando exclusivamente sus propios ítems una
    vez que empiecen a existir ítems de auto. Con `auto_id`: solo los de
    ese auto.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        query = (
            session.query(ItemMantenimiento)
            .options(selectinload(ItemMantenimiento.materiales))
            .filter(ItemMantenimiento.casa_id == casa_id)
        )
        if auto_id is None:
            query = query.filter(ItemMantenimiento.auto_id.is_(None))
        else:
            query = query.filter(ItemMantenimiento.auto_id == auto_id)
        return query.order_by(ItemMantenimiento.creado_en).all()
    finally:
        session.close()


def completar_item(casa_id: UUID, item_id: UUID, actor: UUID) -> ItemMantenimiento:
    """Marca un ítem como "completado" (REQ-004).

    Rechaza completar un ítem ya completado (`ConflictError`). Si es
    recurrente y su `fecha_estimada` todavía no llegó, rechaza con
    `ConflictError` (TC-007) — mismo gate recién agregado a
    `tarea_service.completar_tarea`. Si es recurrente, genera una nueva
    instancia "pendiente" con `fecha_estimada` = fecha estimada actual +
    `_DIAS_POR_PERIODICIDAD[periodicidad]` días (TC-006); si no, no genera
    nada (TC-005).
    """
    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        item = _obtener_item_o_none(session, casa_id, item_id)
        if item is None:
            raise NotFoundError(f"El ítem de mantenimiento {item_id} no existe en la casa {casa_id}.")

        if item.estado == "completado":
            raise ConflictError(f"El ítem de mantenimiento {item_id} ya fue completado.")

        if (
            item.recurrente
            and item.fecha_estimada is not None
            and date.today() < item.fecha_estimada
        ):
            raise ConflictError(
                f"Este ítem recurrente todavía no se puede completar — está programado "
                f"para {item.fecha_estimada.isoformat()}."
            )

        item.estado = "completado"

        if item.recurrente:
            dias = _DIAS_POR_PERIODICIDAD.get(item.periodicidad)
            nueva_fecha = item.fecha_estimada + timedelta(days=dias) if dias is not None else None
            nuevo = ItemMantenimiento(
                id=uuid.uuid4(),
                casa_id=item.casa_id,
                nombre=item.nombre,
                descripcion=item.descripcion,
                fecha_estimada=nueva_fecha,
                recurrente=True,
                periodicidad=item.periodicidad,
                estado="pendiente",
            )
            session.add(nuevo)

        session.commit()
        session.refresh(item)
        # Mismo motivo que en `crear_item`: fuerza la carga de `materiales`
        # mientras la sesión sigue abierta, antes de que el `finally` la
        # cierre (`expire_on_commit`, default de `SessionLocal`).
        list(item.materiales)
        return item
    except (PermissionDeniedError, NotFoundError, ConflictError):
        session.rollback()
        raise
    finally:
        session.close()


def obtener_items_con_alerta(casa_id: UUID) -> List[ItemMantenimientoAlerta]:
    """Ítems "pendiente" de `casa_id` cuya `fecha_estimada` está a
    `UMBRAL_ALERTA_DIAS` días o menos, incluidos los ya vencidos
    (REQ-005, TC-008). Un ítem sin `fecha_estimada` nunca genera alerta.
    No valida que `casa_id` exista: si no existe, simplemente no hay
    ningún ítem que iterar (no-op), mismo criterio que
    `tarjeta_service.obtener_tarjetas_con_alerta`.

    Spec `mantenimiento-autos` (REQ-004): sin cambios en el filtro — ya
    incluye ítems de la casa Y de autos, sin distinguir origen (el
    banner de Inicio es uno solo, combinado). Solo se le agrega
    `auto_id`/`auto_nombre` (nullable) al resultado, resolviendo el
    nombre del auto con una única consulta batched (evita N+1) para que
    el frontend arme el texto correcto de cada alerta.
    """
    hoy = date.today()

    session = get_session()
    try:
        items = (
            session.query(ItemMantenimiento)
            .filter(
                ItemMantenimiento.casa_id == casa_id,
                ItemMantenimiento.estado == "pendiente",
                ItemMantenimiento.fecha_estimada.isnot(None),
            )
            .all()
        )

        auto_ids = {item.auto_id for item in items if item.auto_id is not None}
        nombres_por_auto_id = {}
        if auto_ids:
            for auto in session.query(Auto).filter(Auto.id.in_(auto_ids)).all():
                nombres_por_auto_id[auto.id] = f"{auto.marca} {auto.modelo}"

        alertas: List[ItemMantenimientoAlerta] = []
        for item in items:
            dias_para_vencimiento = (item.fecha_estimada - hoy).days
            if dias_para_vencimiento <= UMBRAL_ALERTA_DIAS:
                alertas.append(
                    ItemMantenimientoAlerta(
                        id=item.id,
                        nombre=item.nombre,
                        fecha_estimada=item.fecha_estimada,
                        dias_para_vencimiento=dias_para_vencimiento,
                        vencido=dias_para_vencimiento < 0,
                        auto_id=item.auto_id,
                        auto_nombre=nombres_por_auto_id.get(item.auto_id),
                    )
                )
        return alertas
    finally:
        session.close()
