"""Servicio de Casa: creación de casas (REQ-001), descubrimiento de casas
por Usuario (`listar_casas_de_usuario`, spec `usuarios-auth`) y meta de
puntos mensual de la casa (spec `gamificacion-puntos`, REQ-005)."""
import uuid
from typing import List, Optional
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.miembro import Miembro, RolEnum
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import _validar_actor_admin


def crear_casa(nombre: str, usuario_id: UUID) -> Casa:
    """Crea una Casa nueva y registra a `usuario_id` como su primer
    miembro con rol Administrador (REQ-001, TC-001).

    Rechaza nombres vacíos o solo espacios (TC-002).

    Nota de diseño (spec `usuarios-auth`, REQ-004): el `Miembro`
    administrador creado recibe un `id` propio (`uuid.uuid4()`), NO
    `usuario_id` — antes de esta spec, cuando cada persona tenía a lo
    sumo una Casa, se usaba directamente `usuario_creador` como
    `Miembro.id`. Eso ya no es válido: un mismo Usuario puede crear más
    de una Casa (TC-007), y `Miembro.id` es la clave primaria global de
    la tabla `miembros` — no puede repetirse entre casas. El vínculo con
    la identidad real ahora vive en la FK `Miembro.usuario_id`. Se sigue
    usando un nombre de miembro por defecto y `str(usuario_id)` como
    identificación inicial (única por construcción dentro de esa Casa,
    al ser su primer miembro); ambos son editables más adelante vía
    `agregar_miembro`/futuras specs de perfil sin afectar este contrato.
    """
    if nombre is None or not str(nombre).strip():
        raise ValidationError("El nombre de la casa no puede estar vacío.")

    session = get_session()
    try:
        casa = Casa(id=uuid.uuid4(), nombre=nombre.strip())
        session.add(casa)
        session.flush()

        admin = Miembro(
            id=uuid.uuid4(),
            casa_id=casa.id,
            usuario_id=usuario_id,
            nombre="Administrador",
            identificacion=str(usuario_id),
            rol=RolEnum.ADMIN,
            activo=True,
        )
        session.add(admin)
        session.commit()
        session.refresh(casa)
        # Fuerza la carga de la relación antes de cerrar la sesión.
        _ = casa.miembros
        return casa
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def listar_casas_de_usuario(usuario_id: UUID) -> List[Casa]:
    """Devuelve las Casas donde `usuario_id` tiene un Miembro activo
    (REQ-006, TC-010) — expuesta vía `GET /casas/mias`, la única ruta de
    descubrimiento de casas por usuario del proyecto.
    """
    session = get_session()
    try:
        casas = (
            session.query(Casa)
            .join(Miembro, Miembro.casa_id == Casa.id)
            .filter(Miembro.usuario_id == usuario_id, Miembro.activo.is_(True))
            .all()
        )
        for casa in casas:
            # Fuerza la carga de la relación antes de cerrar la sesión.
            _ = casa.miembros
        return casas
    finally:
        session.close()


def actualizar_meta_puntos(casa_id: UUID, meta: Optional[int], actor: UUID) -> Casa:
    """Configura (o desactiva, con `meta=None`) la meta de puntos mensual
    de `casa_id` (REQ-005, TC-006) — requiere que `actor` sea
    Administrador activo de esa casa, mismo guard que otras acciones de
    casa (`_validar_actor_admin`, `[SERV-03]`)."""
    if meta is not None and (isinstance(meta, bool) or not isinstance(meta, int) or meta < 0):
        raise ValidationError("La meta de puntos debe ser un entero no negativo, o None.")

    session = get_session()
    try:
        casa = session.get(Casa, casa_id)
        if casa is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        _validar_actor_admin(session, casa_id, actor)

        casa.meta_puntos_mensual = meta
        session.commit()
        session.refresh(casa)
        # Fuerza la carga de la relación antes de cerrar la sesión — mismo
        # criterio que `crear_casa` (`CasaOut.miembros` la necesita
        # serializada, y la sesión ya está cerrada para cuando eso pasa).
        _ = casa.miembros
        return casa
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()
