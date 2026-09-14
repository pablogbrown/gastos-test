"""Servicio de Casa: creación de casas (REQ-001) y descubrimiento de casas
por Usuario (`listar_casas_de_usuario`, spec `usuarios-auth`)."""
import uuid
from typing import List
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.miembro import Miembro, RolEnum
from src.services.exceptions import ValidationError


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
