"""Servicio de Suscripcion: alta, listado, cancelación y generación
perezosa de los gastos mensuales (spec `gastos-suscripcion-mensual`).

Cubre REQ-001 (crear + generar de inmediato el gasto del mes actual),
REQ-002 (generación perezosa al listar gastos, sin duplicar ni
reconstruir meses pasados), REQ-003 (cancelar es hacia adelante, nunca
retroactivo) y REQ-004 (solo un Administrador puede crear o cancelar,
mismo criterio que `_validar_actor_admin` de `miembro_service`).

Diseño (Design Rationale de T2): `generar_gastos_pendientes` vive acá
(dueño de la regla "qué mes le toca a esta suscripción"), pero delega en
`gasto_service.registrar_gasto` para el efecto real — este servicio
nunca reimplementa cómo se reparte un gasto entre participantes, que es
responsabilidad exclusiva de `gasto_service` (un-servicio-por-
responsabilidad, mismo principio ya establecido en el proyecto).
"""
import uuid
from datetime import date
from typing import List, Optional, Tuple
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.categoria import Categoria
from src.db.models.miembro import RolEnum
from src.db.models.suscripcion import Suscripcion
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.gasto_service import MONEDAS_VALIDAS
from src.services.miembro_service import _obtener_miembro_o_none, _validar_actor_admin


def _mes_actual() -> str:
    hoy = date.today()
    return f"{hoy.year:04d}-{hoy.month:02d}"


def crear_suscripcion(
    casa_id: UUID,
    descripcion: str,
    importe,
    categoria_id: Optional[UUID],
    actor: UUID,
    moneda: str = "ARS",
) -> Suscripcion:
    """Crea una Suscripcion activa y genera de inmediato el gasto del mes
    actual (REQ-001). Requiere que `actor` sea Administrador activo de la
    casa (REQ-004).

    El gasto generado se reparte entre los miembros activos igual que un
    gasto normal (misma lógica de `gasto_service.registrar_gasto`, sin
    selección de participantes al crear la suscripción).

    `moneda` (spec `gastos-multi-moneda`, REQ-004/REQ-006): `"ARS"`
    (default) o `"USD"` — fija desde la creación (no hay endpoint de
    edición hoy); cada gasto que esta suscripción genere mensualmente
    hereda esta misma moneda.
    """
    # Import diferido: evita el ciclo `gasto_service` -> `suscripcion_service`
    # (`listar_gastos` importa este módulo dentro de la función, ver ahí).
    from src.services.gasto_service import registrar_gasto

    if not descripcion or not str(descripcion).strip():
        raise ValidationError("La descripción de la suscripción no puede estar vacía.")
    if importe is None or float(importe) <= 0:
        raise ValidationError("El importe de la suscripción debe ser mayor a cero.")
    if categoria_id is None:
        raise ValidationError("La suscripción debe tener una categoría asignada.")
    if moneda not in MONEDAS_VALIDAS:
        raise ValidationError(f"Moneda inválida: {moneda!r}. Debe ser 'ARS' o 'USD'.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        _validar_actor_admin(session, casa_id, actor)

        categoria = (
            session.query(Categoria)
            .filter(Categoria.id == categoria_id, Categoria.casa_id == casa_id)
            .one_or_none()
        )
        if categoria is None:
            raise ValidationError("La categoría indicada no existe en esta casa.")

        suscripcion = Suscripcion(
            id=uuid.uuid4(),
            casa_id=casa_id,
            descripcion=descripcion.strip(),
            importe=importe,
            categoria_id=categoria_id,
            pagado_por=actor,
            activa=True,
            ultimo_mes_generado=None,
            moneda=moneda,
        )
        session.add(suscripcion)
        session.commit()
        session.refresh(suscripcion)
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()

    # El gasto del mes actual se genera fuera de la transacción de arriba
    # (ya comprometida): `registrar_gasto` abre y maneja su propia sesión
    # — mismo patrón que `generar_gastos_pendientes` más abajo. Si esto
    # fallara, la Suscripcion ya creada quedaría sin su primer gasto, pero
    # nunca huérfana (existe con id válido) — la próxima visita a
    # `listar_gastos` la generaría igual, vía la generación perezosa.
    registrar_gasto(
        casa_id,
        suscripcion.descripcion,
        suscripcion.importe,
        date.today(),
        suscripcion.categoria_id,
        suscripcion.pagado_por,
        actor,
        suscripcion_id=suscripcion.id,
        moneda=suscripcion.moneda,
        # Spec `gastos-estado-pago`, REQ-003: un cargo automatico de
        # suscripcion nunca nace "pagado" -- nadie confirmo todavia que
        # esta saldado.
        estado="a_pagar",
    )

    session = get_session()
    try:
        suscripcion_actualizada = session.get(Suscripcion, suscripcion.id)
        suscripcion_actualizada.ultimo_mes_generado = _mes_actual()
        session.commit()
        session.refresh(suscripcion_actualizada)
        return suscripcion_actualizada
    finally:
        session.close()


def _mes_de(fecha: date) -> str:
    return f"{fecha.year:04d}-{fecha.month:02d}"


def registrar_suscripcion_detectada(
    casa_id: UUID,
    descripcion: str,
    importe,
    categoria_id: Optional[UUID],
    pagado_por: UUID,
    actor: UUID,
    moneda: str,
    fecha: date,
    tarjeta_id: Optional[UUID] = None,
) -> Tuple[Optional[Suscripcion], bool]:
    """Vincula una línea de consumo de un comercio reconocido (Netflix,
    Spotify, Disney+) a una Suscripcion de la casa — spec `importar-
    resumen-tarjeta`, REQ-004.

    A diferencia de `crear_suscripcion` (que genera de inmediato un gasto
    fechado "hoy" además de crear la Suscripcion), esta función registra
    el gasto con la fecha/importe/moneda REALES del resumen — nunca "hoy"
    — y dejar `ultimo_mes_generado` en el mes de esa fecha para que la
    generación perezosa mensual (`generar_gastos_pendientes`) no lo
    duplique después.

    Devuelve `(Suscripcion, False)` si encontró o creó una Suscripcion
    (el gasto ya quedó registrado y vinculado dentro de esta misma
    llamada — el caller no necesita registrarlo de nuevo). Devuelve
    `(None, True)` cuando no existía una Suscripcion activa con esa
    descripción y `actor` no es Administrador de la casa: crear una
    Suscripcion nueva requiere Administrador (REQ-004); en ese caso NO se
    registra ningún gasto acá — el `bool=True` le indica al caller
    (`resumen_importer_service`) que esa línea debe importarse como un
    gasto suelto en su lugar, sin abortar el resto de la importación.
    """
    # Import diferido: mismo motivo que `crear_suscripcion` (evita el
    # ciclo `gasto_service` -> `suscripcion_service`).
    from src.services.gasto_service import registrar_gasto

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        descripcion_normalizada = descripcion.strip()
        existente = (
            session.query(Suscripcion)
            .filter(Suscripcion.casa_id == casa_id, Suscripcion.activa.is_(True))
            .filter(Suscripcion.descripcion.ilike(descripcion_normalizada))
            .one_or_none()
        )

        if existente is not None:
            suscripcion_id = existente.id
        else:
            actor_miembro = _obtener_miembro_o_none(session, casa_id, actor)
            es_administrador = (
                actor_miembro is not None
                and actor_miembro.activo
                and actor_miembro.rol == RolEnum.ADMIN
            )
            if not es_administrador:
                return None, True

            nueva = Suscripcion(
                id=uuid.uuid4(),
                casa_id=casa_id,
                descripcion=descripcion_normalizada,
                importe=importe,
                categoria_id=categoria_id,
                pagado_por=pagado_por,
                activa=True,
                ultimo_mes_generado=None,
                moneda=moneda,
            )
            session.add(nueva)
            session.commit()
            session.refresh(nueva)
            suscripcion_id = nueva.id
    except NotFoundError:
        session.rollback()
        raise
    finally:
        session.close()

    registrar_gasto(
        casa_id,
        descripcion_normalizada,
        importe,
        fecha,
        categoria_id,
        pagado_por,
        actor,
        suscripcion_id=suscripcion_id,
        moneda=moneda,
        tarjeta_id=tarjeta_id,
        # Spec `gastos-estado-pago`, REQ-004: el resumen recien se
        # importo -- el usuario todavia no pago esa tarjeta.
        estado="a_pagar",
    )

    session = get_session()
    try:
        suscripcion_actualizada = session.get(Suscripcion, suscripcion_id)
        suscripcion_actualizada.ultimo_mes_generado = _mes_de(fecha)
        session.commit()
        session.refresh(suscripcion_actualizada)
        return suscripcion_actualizada, False
    finally:
        session.close()


def listar_suscripciones(casa_id: UUID) -> List[Suscripcion]:
    """Todas las suscripciones (activas e inactivas) de una casa."""
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        return (
            session.query(Suscripcion)
            .filter(Suscripcion.casa_id == casa_id)
            .order_by(Suscripcion.creado_en)
            .all()
        )
    finally:
        session.close()


def cancelar_suscripcion(casa_id: UUID, suscripcion_id: UUID, actor: UUID) -> Suscripcion:
    """Marca `activa=False` (REQ-003) — detiene la generación de gastos
    futuros. Nunca toca ningún Gasto ya generado: cancelar es hacia
    adelante, nunca retroactivo. Requiere Administrador (REQ-004)."""
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        _validar_actor_admin(session, casa_id, actor)

        suscripcion = (
            session.query(Suscripcion)
            .filter(Suscripcion.casa_id == casa_id, Suscripcion.id == suscripcion_id)
            .one_or_none()
        )
        if suscripcion is None:
            raise NotFoundError(f"La suscripción {suscripcion_id} no existe en la casa {casa_id}.")

        suscripcion.activa = False
        session.commit()
        session.refresh(suscripcion)
        return suscripcion
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def generar_gastos_pendientes(casa_id: UUID) -> None:
    """Para cada Suscripcion activa de `casa_id` cuyo `ultimo_mes_
    generado` no sea el mes actual, genera el gasto correspondiente vía
    `gasto_service.registrar_gasto` y actualiza `ultimo_mes_generado`
    (REQ-002). Genera como máximo un gasto por suscripción por mes; nunca
    duplica el del mes ya generado, y nunca reconstruye retroactivamente
    meses en los que nadie visitó la casa (limitación conocida y
    aceptada del diseño perezoso).

    Llamada por `gasto_service.listar_gastos` como primera línea — cubre
    tanto la pantalla Gastos como el Inicio (que ya llama a `listar_
    gastos` internamente), sin un segundo punto de enganche. No valida
    que `casa_id` exista: si no existe, simplemente no hay Suscripcion
    alguna que iterar (no-op) — la validación de "casa existe" sigue
    siendo responsabilidad exclusiva de `listar_gastos`.

    `moneda` (spec `gastos-multi-moneda`, REQ-004): cada gasto generado
    hereda la `moneda` de su Suscripcion — nunca la de otra.
    """
    from src.services.gasto_service import registrar_gasto

    mes_actual = _mes_actual()

    session = get_session()
    try:
        pendientes = (
            session.query(Suscripcion)
            .filter(Suscripcion.casa_id == casa_id, Suscripcion.activa.is_(True))
            .filter(
                (Suscripcion.ultimo_mes_generado.is_(None))
                | (Suscripcion.ultimo_mes_generado != mes_actual)
            )
            .all()
        )
        # Datos leídos y liberados de esta sesión antes de llamar a
        # `registrar_gasto` (que abre la suya propia) — evita anidar
        # sesiones/transacciones sobre el mismo engine.
        datos_pendientes = [
            (s.id, s.descripcion, s.importe, s.categoria_id, s.pagado_por, s.moneda)
            for s in pendientes
        ]
    finally:
        session.close()

    for suscripcion_id, descripcion, importe, categoria_id, pagado_por, moneda in datos_pendientes:
        registrar_gasto(
            casa_id,
            descripcion,
            importe,
            date.today(),
            categoria_id,
            pagado_por,
            pagado_por,
            suscripcion_id=suscripcion_id,
            moneda=moneda,
            # Spec `gastos-estado-pago`, REQ-003: idem `crear_suscripcion`.
            estado="a_pagar",
        )

        session = get_session()
        try:
            suscripcion = session.get(Suscripcion, suscripcion_id)
            if suscripcion is not None:
                suscripcion.ultimo_mes_generado = mes_actual
                session.commit()
        finally:
            session.close()
