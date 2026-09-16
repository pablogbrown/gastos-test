"""Servicio de Auto: alta y listado (spec `mantenimiento-autos`, REQ-001).

Sin edición ni borrado en esta spec — alta y listado alcanzan para el
caso de uso (ver `00-overview.md`'s API/Data Contracts). Sin guard de rol
adicional (a diferencia de `suscripcion_service`, que requiere
Administrador): "cualquier miembro activo de la casa puede registrarlo y
verlo" (REQ-001) — mismo criterio que `tarjeta_service.crear_tarjeta` vía
`requiere_membresia_activa` ([SERV-03]).
"""
import uuid
from typing import List
from uuid import UUID

from src.db.base import get_session
from src.db.models.auto import Auto
from src.db.models.casa import Casa
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import requiere_membresia_activa


def crear_auto(
    casa_id: UUID,
    marca: str,
    modelo: str,
    actor: UUID,
    patente=None,
    anio=None,
) -> Auto:
    """Registra un auto de la casa (REQ-001, TC-001). `marca`/`modelo`
    obligatorios; `patente`/`anio` opcionales."""
    if not marca or not str(marca).strip():
        raise ValidationError("La marca del auto no puede estar vacía.")
    if not modelo or not str(modelo).strip():
        raise ValidationError("El modelo del auto no puede estar vacío.")

    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        auto = Auto(
            id=uuid.uuid4(),
            casa_id=casa_id,
            marca=marca.strip(),
            modelo=modelo.strip(),
            patente=patente.strip() if patente else None,
            anio=anio,
        )
        session.add(auto)
        session.commit()
        session.refresh(auto)
        return auto
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def listar_autos(casa_id: UUID) -> List[Auto]:
    """Lista los autos de la casa."""
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return (
            session.query(Auto)
            .filter(Auto.casa_id == casa_id)
            .order_by(Auto.creado_en)
            .all()
        )
    finally:
        session.close()
