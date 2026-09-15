"""Servicio de Miembro: alta, baja y guard de membresía activa.

Cubre REQ-002, REQ-003, REQ-005 (`casas-miembros`) y expone
`requiere_membresia_activa`, el guard transversal que las specs `gastos`
y `tareas-puntos` importan directamente para cumplir REQ-005 (nadie opera
sin ser miembro activo).

`resolver_actor_en_casa` (spec `usuarios-auth`) es un guard adicional y
distinto: traduce la identidad global resuelta del JWT (`Usuario`) al
`Miembro.id` correspondiente dentro de una Casa puntual, para la capa de
rutas (T3). Ninguno de los dos reemplaza al otro.
"""
import uuid
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.historial_actividad import TipoActividadEnum
from src.db.models.miembro import Miembro, RolEnum
from src.db.models.usuario import Usuario
from src.services.actividad_service import registrar_actividad
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError


def _obtener_miembro_o_none(session, casa_id: UUID, miembro_id: UUID):
    return (
        session.query(Miembro)
        .filter(Miembro.casa_id == casa_id, Miembro.id == miembro_id)
        .one_or_none()
    )


def _validar_actor_admin(session, casa_id: UUID, actor: UUID) -> None:
    actor_miembro = _obtener_miembro_o_none(session, casa_id, actor)
    if actor_miembro is None or not actor_miembro.activo:
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")
    if actor_miembro.rol != RolEnum.ADMIN:
        raise PermissionDeniedError("Solo un Administrador puede realizar esta acción.")


def agregar_miembro(
    casa_id: UUID, nombre: str, identificacion: str, email_usuario: str, actor: UUID
) -> Miembro:
    """Agrega un nuevo Miembro (rol `member`) a la casa `casa_id`,
    vinculado al Usuario existente identificado por `email_usuario`
    (spec `usuarios-auth`, REQ-004, TC-008).

    Requiere que `actor` sea Administrador activo de esa casa (TC-006).
    Rechaza identificación duplicada dentro de la misma casa (TC-004),
    delegando la garantía última al constraint único de T1.

    Nota de diseño (spec `usuarios-auth`): antes de esta spec, el cliente
    podía enviar cualquier UUID como identidad del nuevo miembro (sin
    verificación). Ahora se exige un email — y el `Miembro` nuevo queda
    vinculado a su `usuario_id`, nunca a uno creado al vuelo. Esto es lo
    que hace real la regla "un Usuario puede estar en varias Casas": un
    mismo Usuario puede tener múltiples filas `Miembro` (una por Casa),
    todas con el mismo `usuario_id`.

    Nota de diseño (spec `invitar-miembro-pendiente`, REQ-001): si
    `email_usuario` NO corresponde a ningún Usuario registrado, esto ya
    no se rechaza con `NotFoundError` — se crea la membresía igual, en
    estado "pendiente" (`usuario_id=None`, `email_invitacion` guarda el
    email normalizado). `registrar_usuario` la vincula automáticamente
    más adelante (`vincular_membresias_pendientes`), cuando esa persona
    se registre con ese mismo email.
    """
    if not nombre or not str(nombre).strip():
        raise ValidationError("El nombre del miembro no puede estar vacío.")
    if not identificacion or not str(identificacion).strip():
        raise ValidationError("La identificación del miembro no puede estar vacía.")
    if not email_usuario or not str(email_usuario).strip():
        raise ValidationError("El email del usuario a agregar no puede estar vacío.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        _validar_actor_admin(session, casa_id, actor)

        email_normalizado = email_usuario.strip().lower()
        usuario = (
            session.query(Usuario).filter(Usuario.email == email_normalizado).one_or_none()
        )

        if usuario is not None:
            # Fix `fix-membresia-duplicada-actor` (REQ-001): un mismo Usuario
            # no puede tener más de una fila Miembro activa en la misma casa
            # — esto es lo que antes permitía que `resolver_actor_en_casa`
            # encontrara más de una fila y crasheara con
            # `MultipleResultsFound` (500). `.one_or_none()` es correcto acá
            # (a diferencia de T2): antes de ese fix nunca puede existir más
            # de una fila activa para este (casa_id, usuario_id), justo
            # porque esa validación recién se estaba agregando.
            membresia_existente = (
                session.query(Miembro)
                .filter(
                    Miembro.casa_id == casa_id,
                    Miembro.usuario_id == usuario.id,
                    Miembro.activo.is_(True),
                )
                .one_or_none()
            )
            if membresia_existente is not None:
                raise ValidationError("El usuario ya es miembro activo de esta casa.")
        else:
            # spec `invitar-miembro-pendiente` (REQ-003): mismo criterio de
            # "ya es miembro de esta casa", pero para una invitación
            # pendiente (sin Usuario todavía) — evita duplicar la invitación
            # mientras siga sin vincularse.
            invitacion_existente = (
                session.query(Miembro)
                .filter(
                    Miembro.casa_id == casa_id,
                    Miembro.email_invitacion == email_normalizado,
                    Miembro.usuario_id.is_(None),
                )
                .one_or_none()
            )
            if invitacion_existente is not None:
                raise ValidationError("El usuario ya es miembro activo de esta casa.")

        duplicado = (
            session.query(Miembro)
            .filter(Miembro.casa_id == casa_id, Miembro.identificacion == identificacion)
            .one_or_none()
        )
        if duplicado is not None:
            raise ValidationError(
                f"Ya existe un miembro con identificación {identificacion!r} en esta casa."
            )

        miembro = Miembro(
            id=uuid.uuid4(),
            casa_id=casa_id,
            usuario_id=usuario.id if usuario is not None else None,
            email_invitacion=email_normalizado,
            nombre=nombre.strip(),
            identificacion=identificacion.strip(),
            rol=RolEnum.MEMBER,
            activo=True,
        )
        session.add(miembro)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ValidationError(
                f"Ya existe un miembro con identificación {identificacion!r} en esta casa."
            ) from exc
        session.refresh(miembro)

        # Hook de actividad (REQ-001, spec `fix-historial-desactivacion-
        # miembro`): se dispara recién después del commit de arriba, nunca
        # antes, mismo patrón que `gasto_service`/`tarea_service` — así una
        # entrada de actividad nunca describe un alta que en definitiva no
        # llegó a confirmarse.
        registrar_actividad(
            casa_id,
            TipoActividadEnum.MIEMBRO_AGREGADO,
            miembro.id,
            f"{miembro.nombre} fue agregado a la casa.",
        )

        return miembro
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def desactivar_miembro(casa_id: UUID, miembro_id: UUID, actor: UUID) -> Miembro:
    """Marca `activo=False` en el miembro indicado (REQ-003, TC-005).

    No borra ni toca el historial de gastos/tareas asociado — solo cambia
    el flag `activo`. Requiere que `actor` sea Administrador activo.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        _validar_actor_admin(session, casa_id, actor)

        miembro = _obtener_miembro_o_none(session, casa_id, miembro_id)
        if miembro is None:
            raise NotFoundError(f"El miembro {miembro_id} no existe en la casa {casa_id}.")

        miembro.activo = False
        session.commit()
        session.refresh(miembro)

        # Hook de actividad (REQ-002, spec `fix-historial-desactivacion-
        # miembro`): se dispara recién después del commit de arriba, nunca
        # antes, mismo patrón que `gasto_service`/`tarea_service` — así una
        # entrada de actividad nunca describe una baja que en definitiva no
        # llegó a confirmarse.
        registrar_actividad(
            casa_id,
            TipoActividadEnum.MIEMBRO_DESACTIVADO,
            miembro.id,
            f"{miembro.nombre} fue desactivado.",
        )

        return miembro
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def vincular_membresias_pendientes(session, usuario_id: UUID, email: str) -> None:
    """Vincula todas las membresías `Miembro` pendientes que coincidan con
    `email` al `Usuario` recién registrado `usuario_id` (spec
    `invitar-miembro-pendiente`, REQ-002).

    A diferencia de cada otra función de este módulo, ESTA NO abre su
    propia sesión — recibe una ya abierta y no hace `commit`/`close`. Es
    deliberado: se llama desde `auth_service.registrar_usuario`, DENTRO
    de la misma transacción que crea el `Usuario`, para que el alta y la
    vinculación de sus membresías pendientes sean atómicas (si el
    registro falla, ninguna vinculación queda a medio hacer). El llamador
    es responsable de normalizar `email` y de hacer `commit()`.

    Vincula TODAS las filas pendientes con ese email, en cualquier casa
    (REQ-002) — un mismo Usuario puede tener sido invitado a varias casas
    a la vez.
    """
    (
        session.query(Miembro)
        .filter(Miembro.email_invitacion == email, Miembro.usuario_id.is_(None))
        .update({Miembro.usuario_id: usuario_id}, synchronize_session=False)
    )


def listar_miembros(casa_id: UUID):
    """Lista todos los miembros (activos e inactivos) de una casa.

    No forma parte de las "Interfaces Produced" de T2 (ninguna spec
    hermana la consume), pero se agrega aquí para que la ruta GET de T3
    siga siendo un adaptador delgado en vez de consultar el modelo
    directamente.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return session.query(Miembro).filter(Miembro.casa_id == casa_id).all()
    finally:
        session.close()


def requiere_membresia_activa(casa_id: UUID, usuario_id: UUID) -> bool:
    """Guard transversal (REQ-005): True si `usuario_id` es miembro activo
    de `casa_id`. Reutilizado por las specs `gastos` y `tareas-puntos`
    antes de permitir registrar un gasto o completar una tarea (TC-008).

    Nota (spec `usuarios-auth`): a pesar del nombre del parámetro, esta
    función NO cambia con `usuarios-auth` — sigue recibiendo un
    `Miembro.id` (la identidad dentro de esa casa puntual), exactamente
    como la llaman hoy `gasto_service`/`tarea_service`. La resolución de
    la identidad *global* (`Usuario`, JWT) a un `Miembro.id` por casa vive
    en `resolver_actor_en_casa`, más abajo — un guard nuevo y distinto,
    usado solo por la capa de rutas (T3).
    """
    session = get_session()
    try:
        miembro = _obtener_miembro_o_none(session, casa_id, usuario_id)
        return miembro is not None and miembro.activo
    finally:
        session.close()


def resolver_actor_en_casa(casa_id: UUID, usuario_id: UUID) -> UUID:
    """Traduce la identidad global de un Usuario autenticado (JWT,
    `usuario_id`) al `Miembro.id` que le corresponde dentro de `casa_id`
    (spec `usuarios-auth`, REQ-003/REQ-005).

    Es el puente entre `get_current_usuario` (que solo conoce el
    `Usuario` global) y los servicios ya existentes de esta y otras specs
    (`casa_service`, `gasto_service`, `tarea_service`, ...), que siguen
    sin cambios: todos ellos reciben y usan un `Miembro.id` como `actor`,
    nunca un `usuario_id` global.

    Lanza `NotFoundError` (404) si la casa no existe, y
    `PermissionDeniedError` (403) si el Usuario no tiene un Miembro activo
    en ella (TC-009) — el mismo caso que `requiere_membresia_activa`
    devolviendo False, pero acá se necesita el id concreto del Miembro,
    no solo el booleano.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        # Fix `fix-membresia-duplicada-actor` (REQ-002): `.one_or_none()`
        # asume que nunca hay más de una fila Miembro activa para este
        # (casa_id, usuario_id) — T1 impide que se CREEN nuevas duplicadas,
        # pero un dato preexistente a este fix (o cualquier vía no
        # anticipada) puede seguir violando esa asunción. `.first()` nunca
        # lanza `MultipleResultsFound`: devuelve `None` si no hay filas, o
        # la primera según `order_by`, sin importar cuántas existan.
        # `Miembro` no tiene columna de fecha de creación (no se agrega una
        # solo para este caso defensivo) — `order_by(Miembro.id)` da un
        # orden estable y determinístico (mismo resultado en cada corrida),
        # aunque arbitrario respecto a cuál membresía es la "correcta": el
        # objetivo acá es eliminar el 500, no arbitrar intención de negocio.
        miembro = (
            session.query(Miembro)
            .filter(
                Miembro.casa_id == casa_id,
                Miembro.usuario_id == usuario_id,
                Miembro.activo.is_(True),
            )
            .order_by(Miembro.id)
            .first()
        )
        if miembro is None:
            raise PermissionDeniedError("El usuario no es miembro activo de esta casa.")
        return miembro.id
    finally:
        session.close()
