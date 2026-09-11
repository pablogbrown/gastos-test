"""Servicio de Casa: creación de casas (REQ-001)."""
import uuid
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.miembro import Miembro, RolEnum
from src.services.exceptions import ValidationError


def crear_casa(nombre: str, usuario_creador: UUID) -> Casa:
    """Crea una Casa nueva y registra a `usuario_creador` como su primer
    miembro con rol Administrador (REQ-001, TC-001).

    Rechaza nombres vacíos o solo espacios (TC-002).

    Nota de diseño: la firma de este servicio (fijada por T2's
    "Interfaces Produced") no recibe el nombre personal de
    `usuario_creador` (eso vive en el dominio de auth, fuera de esta
    spec). Se usa un nombre de miembro por defecto y `str(usuario_creador)`
    como identificación inicial (única por construcción, al ser el primer
    miembro de la casa); ambos son editables más adelante vía
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
            id=usuario_creador,
            casa_id=casa.id,
            nombre="Administrador",
            identificacion=str(usuario_creador),
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
