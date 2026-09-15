"""Servicio de Categoría: catálogo de categorías de gasto por casa (REQ-002).

`crear_categoria` es la única operación de escritura sobre el catálogo:
solo un Administrador activo de la casa puede invocarla (TC-003), vía la
misma tabla de permisos (`src/services/permisos.py`) que usa
`casas-miembros` — no se define una regla de rol propia aquí.
"""
import uuid
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.categoria import Categoria
from src.db.models.miembro import Miembro
from src.services import permisos
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError


def _obtener_miembro_o_none(session, casa_id: UUID, miembro_id: UUID):
    return (
        session.query(Miembro)
        .filter(Miembro.casa_id == casa_id, Miembro.id == miembro_id)
        .one_or_none()
    )


def crear_categoria(casa_id: UUID, nombre: str, actor: UUID) -> Categoria:
    """Crea una Categoria nueva en el catálogo de `casa_id` (REQ-002).

    Requiere que `actor` sea un miembro activo con permiso
    `gestionar_categorias` (rol Administrador, TC-003). Rechaza nombres
    vacíos y nombres duplicados dentro de la misma casa.
    """
    if not nombre or not str(nombre).strip():
        raise ValidationError("El nombre de la categoría no puede estar vacío.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        actor_miembro = _obtener_miembro_o_none(session, casa_id, actor)
        if actor_miembro is None or not actor_miembro.activo:
            raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")
        if not permisos.puede(actor_miembro.rol, "gestionar_categorias"):
            raise PermissionDeniedError(
                "Solo un Administrador puede gestionar el catálogo de categorías."
            )

        nombre_normalizado = nombre.strip()
        duplicada = (
            session.query(Categoria)
            .filter(Categoria.casa_id == casa_id, Categoria.nombre == nombre_normalizado)
            .one_or_none()
        )
        if duplicada is not None:
            raise ValidationError(
                f"Ya existe una categoría {nombre_normalizado!r} en esta casa."
            )

        categoria = Categoria(id=uuid.uuid4(), casa_id=casa_id, nombre=nombre_normalizado)
        session.add(categoria)
        session.commit()
        session.refresh(categoria)
        return categoria
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def listar_categorias(casa_id: UUID):
    """Lista el catálogo completo de categorías de una casa."""
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return session.query(Categoria).filter(Categoria.casa_id == casa_id).all()
    finally:
        session.close()


def obtener_o_crear_categoria(casa_id: UUID, nombre: str, actor: UUID) -> Categoria:
    """Find-or-create de una categoría por nombre (case-insensitive) —
    spec `importar-resumen-tarjeta`: usada para asignar la categoría
    "Importado" a todo gasto de un resumen sin categoría inferible del
    PDF, sin duplicar la fila si ya existe (a diferencia de `crear_
    categoria`, que rechaza un nombre duplicado con `ValidationError`).

    A diferencia de `crear_categoria`, no exige rol Administrador: la
    importación de un resumen ya validó sus propios permisos aguas
    arriba (`resumen_importer_service`); esta función es un detalle de
    implementación interno, no una operación de catálogo expuesta al
    usuario.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        nombre_normalizado = nombre.strip()
        existente = (
            session.query(Categoria)
            .filter(Categoria.casa_id == casa_id)
            .filter(Categoria.nombre.ilike(nombre_normalizado))
            .one_or_none()
        )
        if existente is not None:
            return existente

        categoria = Categoria(id=uuid.uuid4(), casa_id=casa_id, nombre=nombre_normalizado)
        session.add(categoria)
        session.commit()
        session.refresh(categoria)
        return categoria
    except NotFoundError:
        session.rollback()
        raise
    finally:
        session.close()
