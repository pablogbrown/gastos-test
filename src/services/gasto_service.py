"""Servicio de Gasto: registro y división entre participantes.

Cubre REQ-001 (registro), REQ-003 (participantes por defecto/explícitos),
REQ-004 (división en partes iguales), REQ-007 (los participantes quedan
fijos al momento del registro) y REQ-008 (historial).

Toda operación de registro llama a `requiere_membresia_activa` — el
guard transversal de la spec `casas-miembros` — exactamente como sus
propios servicios lo exponen para las specs dependientes.

Spec `gastos-en-cuotas`: `registrar_gasto` acepta un `cuotas` opcional
para repartir un gasto grande en N gastos mensuales consecutivos (ver
`_generar_cuotas`/`_sumar_meses` más abajo).

Spec `gastos-suscripcion-mensual`: `registrar_gasto` acepta también un
`suscripcion_id` opcional, independiente de `cuotas` (un gasto generado
por una suscripción nunca tiene `cuotas`, y viceversa) — puramente de
etiquetado, para vincular el `Gasto` resultante a la `Suscripcion` que lo
generó. `listar_gastos` llama a `suscripcion_service.
generar_gastos_pendientes` como primera línea, antes de la query
existente, para que las pantallas Gastos e Inicio disparen la generación
perezosa del mes actual sin necesitar un scheduler nuevo.
"""
import calendar
import uuid
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable, List, Optional
from uuid import UUID

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.categoria import Categoria
from src.db.models.gasto import Gasto, GastoParticipante
from src.db.models.historial_actividad import TipoActividadEnum
from src.db.models.miembro import Miembro
from src.services.actividad_service import registrar_actividad
from src.services.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from src.services.miembro_service import requiere_membresia_activa

# Spec `gastos-multi-moneda`, REQ-006: únicos valores válidos de `moneda`
# para un Gasto o una Suscripcion — hardcodeados acá (no una entidad de
# catálogo, ver Design Rationale de T1) en vez de en `balance_service.py`
# porque este módulo es el punto de entrada de validación (`registrar_
# gasto`); `suscripcion_service.py` reutiliza esta misma constante.
MONEDAS_VALIDAS = {"ARS", "USD"}


def registrar_gasto(
    casa_id: UUID,
    descripcion: str,
    importe,
    fecha,
    categoria_id: Optional[UUID],
    pagado_por: UUID,
    actor: UUID,
    participantes: Optional[Iterable[UUID]] = None,
    cuotas: Optional[int] = None,
    suscripcion_id: Optional[UUID] = None,
    moneda: str = "ARS",
    tarjeta_id: Optional[UUID] = None,
) -> Gasto:
    """Registra un Gasto y sus GastoParticipante asociados.

    `participantes=None` (o vacío) aplica el gasto a todos los miembros
    activos de la casa al momento del registro (REQ-003/TC-004); una
    lista explícita restringe la división a esos miembros (TC-005). El
    importe se divide en partes iguales, ajustando el redondeo en el
    último participante (REQ-004/TC-006).

    `cuotas` (spec `gastos-en-cuotas`, REQ-001 a REQ-004): un entero
    ≥ 2 crea esa cantidad de gastos consecutivos, uno por mes, cada uno
    por el importe total dividido en partes iguales (ajuste de redondeo
    en la última — mismo criterio que entre participantes) y
    compartiendo un `cuota_grupo_id`. `cuotas` ausente, `None`, o
    explícitamente `1` se comporta exactamente igual que hoy (REQ-003):
    un único Gasto, sin ningún dato de cuota poblado. Solo `0` o un
    valor negativo, enviados explícitamente, son rechazados (REQ-004).

    `suscripcion_id` (spec `gastos-suscripcion-mensual`): puramente de
    etiquetado — un gasto generado por una suscripción nunca combina con
    `cuotas` (`suscripcion_service` nunca los pasa juntos).

    `moneda` (spec `gastos-multi-moneda`, REQ-001/REQ-006): `"ARS"`
    (default) o `"USD"` — cualquier otro valor es rechazado. Todas las
    cuotas de una misma compra comparten la `moneda` del gasto original
    (REQ-005/TC-007).

    `tarjeta_id` (spec `importar-resumen-tarjeta`): puramente de
    etiquetado, sin validación adicional — `None` (default) es un gasto
    no originado en una importación de resumen; identifica de qué
    `TarjetaCredito` vino el consumo cuando sí lo es.
    """
    if cuotas is not None and cuotas <= 0:
        raise ValidationError("La cantidad de cuotas debe ser 2 o mayor.")
    generar_en_cuotas = cuotas is not None and cuotas >= 2

    if not descripcion or not str(descripcion).strip():
        raise ValidationError("La descripción del gasto no puede estar vacía.")
    if importe is None or Decimal(str(importe)) <= 0:
        raise ValidationError("El importe del gasto debe ser mayor a cero.")
    if categoria_id is None:
        raise ValidationError("El gasto debe tener una categoría asignada.")
    if moneda not in MONEDAS_VALIDAS:
        raise ValidationError(f"Moneda inválida: {moneda!r}. Debe ser 'ARS' o 'USD'.")

    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        categoria = (
            session.query(Categoria)
            .filter(Categoria.id == categoria_id, Categoria.casa_id == casa_id)
            .one_or_none()
        )
        if categoria is None:
            raise ValidationError("La categoría indicada no existe en esta casa.")

        pagador = (
            session.query(Miembro)
            .filter(Miembro.casa_id == casa_id, Miembro.id == pagado_por)
            .one_or_none()
        )
        if pagador is None:
            raise NotFoundError(f"El miembro {pagado_por} no existe en la casa {casa_id}.")

        miembros_participantes = _resolver_participantes(session, casa_id, participantes)
        if not miembros_participantes:
            raise ValidationError(
                "No hay miembros activos disponibles para dividir el gasto."
            )

        importe_decimal = Decimal(str(importe)).quantize(Decimal("0.01"))

        if generar_en_cuotas:
            gastos_creados = _crear_gastos_en_cuotas(
                session,
                casa_id,
                descripcion,
                importe_decimal,
                fecha,
                pagado_por,
                categoria_id,
                miembros_participantes,
                cuotas,
                moneda,
                tarjeta_id,
            )
        else:
            gasto = Gasto(
                id=uuid.uuid4(),
                casa_id=casa_id,
                descripcion=descripcion.strip(),
                importe=importe_decimal,
                fecha=fecha,
                pagado_por=pagado_por,
                categoria_id=categoria_id,
                suscripcion_id=suscripcion_id,
                moneda=moneda,
                tarjeta_id=tarjeta_id,
            )
            session.add(gasto)
            session.flush()

            partes = _dividir_importe(importe_decimal, len(miembros_participantes))
            for miembro, parte in zip(miembros_participantes, partes):
                session.add(
                    GastoParticipante(
                        gasto_id=gasto.id, miembro_id=miembro.id, monto_correspondiente=parte
                    )
                )
            gastos_creados = [gasto]

        session.commit()
        for gasto_creado in gastos_creados:
            session.refresh(gasto_creado)
            _ = gasto_creado.participantes  # fuerza la carga antes de cerrar la sesión

        # Hook de actividad (REQ-002/TC-003, spec `dashboard-actividad`):
        # se dispara recién después del commit de arriba, nunca antes,
        # para que la entrada de actividad no describa un gasto que en
        # definitiva no llegó a confirmarse. Una vez por cuota generada
        # (spec `gastos-en-cuotas`) — para un gasto sin cuotas, es
        # exactamente la única llamada de siempre.
        for gasto_creado in gastos_creados:
            registrar_actividad(
                casa_id,
                TipoActividadEnum.GASTO_REGISTRADO,
                pagado_por,
                f"{pagador.nombre} registró un gasto de ${gasto_creado.importe} "
                f"({gasto_creado.descripcion}).",
            )

        return gastos_creados[0]
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def _crear_gastos_en_cuotas(
    session,
    casa_id: UUID,
    descripcion: str,
    importe_decimal: Decimal,
    fecha,
    pagado_por: UUID,
    categoria_id: UUID,
    miembros_participantes,
    cuotas: int,
    moneda: str = "ARS",
    tarjeta_id: Optional[UUID] = None,
) -> List[Gasto]:
    """Crea `cuotas` filas `Gasto`, una por mes consecutivo a partir de
    `fecha`, compartiendo un `cuota_grupo_id` (spec `gastos-en-cuotas`,
    REQ-001/REQ-002). Reutiliza `_dividir_importe` dos veces: una para
    repartir el importe total entre las `cuotas`, y otra vez por cuota
    para repartir esa parte entre `miembros_participantes` — mismo
    criterio de ajuste de redondeo (última parte) en ambos niveles.

    `moneda` (spec `gastos-multi-moneda`, REQ-005/TC-007): se propaga sin
    cambios a las N cuotas generadas — ninguna parte de una misma compra
    puede tener una moneda distinta de las demás.

    `tarjeta_id` (spec `importar-resumen-tarjeta`): se propaga sin
    cambios a las N cuotas generadas, igual que `moneda`.
    """
    partes_cuotas = _dividir_importe(importe_decimal, cuotas)
    cuota_grupo_id = uuid.uuid4()
    gastos_creados: List[Gasto] = []

    for i, parte_cuota in enumerate(partes_cuotas):
        gasto = Gasto(
            id=uuid.uuid4(),
            casa_id=casa_id,
            descripcion=f"{descripcion.strip()} ({i + 1}/{cuotas})",
            importe=parte_cuota,
            fecha=_sumar_meses(fecha, i),
            pagado_por=pagado_por,
            categoria_id=categoria_id,
            cuota_grupo_id=cuota_grupo_id,
            cuota_numero=i + 1,
            cuota_total=cuotas,
            moneda=moneda,
            tarjeta_id=tarjeta_id,
        )
        session.add(gasto)
        session.flush()

        partes_participantes = _dividir_importe(parte_cuota, len(miembros_participantes))
        for miembro, parte_participante in zip(miembros_participantes, partes_participantes):
            session.add(
                GastoParticipante(
                    gasto_id=gasto.id,
                    miembro_id=miembro.id,
                    monto_correspondiente=parte_participante,
                )
            )
        gastos_creados.append(gasto)

    return gastos_creados


def registrar_gasto_cuotas_restantes(
    casa_id: UUID,
    descripcion: str,
    importe_por_cuota,
    fecha_inicio,
    cuota_actual: int,
    cuota_total: int,
    categoria_id: UUID,
    pagado_por: UUID,
    actor: UUID,
    moneda: str = "ARS",
    tarjeta_id: Optional[UUID] = None,
) -> List[Gasto]:
    """Registra solo las cuotas RESTANTES de una compra en curso —
    `cuota_actual` (inclusive) hasta `cuota_total`, una por mes
    consecutivo desde `fecha_inicio` — spec `importar-resumen-tarjeta`,
    REQ-003/TC-004.

    A diferencia de `_crear_gastos_en_cuotas` (que siempre arranca una
    serie nueva de `1..N` dividiendo un importe total), acá el resumen ya
    trae el importe de CADA cuota individual — `importe_por_cuota` se usa
    tal cual, sin dividir, en cada una de las `cuota_total - cuota_actual
    + 1` filas generadas; todas comparten un mismo `cuota_grupo_id` nuevo
    (esta serie de cuotas restantes es su propio grupo, independiente de
    cualquier grupo que ya existiera para las cuotas anteriores, que esta
    spec no tiene forma de conocer ni necesita reconciliar).

    Reutiliza `_sumar_meses`/`_dividir_importe`/`_resolver_participantes`
    — nunca reimplementa el reparto entre participantes ni la aritmética
    de fechas, mismo criterio que el resto de `gasto_service`.
    """
    if cuota_actual is None or cuota_total is None or cuota_actual < 1 or cuota_total < cuota_actual:
        raise ValidationError(
            "cuota_actual/cuota_total inválidos: se requiere 1 <= cuota_actual <= cuota_total."
        )
    if not descripcion or not str(descripcion).strip():
        raise ValidationError("La descripción del gasto no puede estar vacía.")
    if importe_por_cuota is None or Decimal(str(importe_por_cuota)) <= 0:
        raise ValidationError("El importe de cada cuota debe ser mayor a cero.")
    if categoria_id is None:
        raise ValidationError("El gasto debe tener una categoría asignada.")
    if moneda not in MONEDAS_VALIDAS:
        raise ValidationError(f"Moneda inválida: {moneda!r}. Debe ser 'ARS' o 'USD'.")

    if not requiere_membresia_activa(casa_id, actor):
        raise PermissionDeniedError("El actor no es un miembro activo de esta casa.")

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        categoria = (
            session.query(Categoria)
            .filter(Categoria.id == categoria_id, Categoria.casa_id == casa_id)
            .one_or_none()
        )
        if categoria is None:
            raise ValidationError("La categoría indicada no existe en esta casa.")

        pagador = (
            session.query(Miembro)
            .filter(Miembro.casa_id == casa_id, Miembro.id == pagado_por)
            .one_or_none()
        )
        if pagador is None:
            raise NotFoundError(f"El miembro {pagado_por} no existe en la casa {casa_id}.")

        miembros_participantes = _resolver_participantes(session, casa_id, None)
        if not miembros_participantes:
            raise ValidationError(
                "No hay miembros activos disponibles para dividir el gasto."
            )

        importe_decimal = Decimal(str(importe_por_cuota)).quantize(Decimal("0.01"))
        cuota_grupo_id = uuid.uuid4()
        cantidad_restantes = cuota_total - cuota_actual + 1
        gastos_creados: List[Gasto] = []

        for i in range(cantidad_restantes):
            gasto = Gasto(
                id=uuid.uuid4(),
                casa_id=casa_id,
                descripcion=descripcion.strip(),
                importe=importe_decimal,
                fecha=_sumar_meses(fecha_inicio, i),
                pagado_por=pagado_por,
                categoria_id=categoria_id,
                cuota_grupo_id=cuota_grupo_id,
                cuota_numero=cuota_actual + i,
                cuota_total=cuota_total,
                moneda=moneda,
                tarjeta_id=tarjeta_id,
            )
            session.add(gasto)
            session.flush()

            partes_participantes = _dividir_importe(importe_decimal, len(miembros_participantes))
            for miembro, parte_participante in zip(miembros_participantes, partes_participantes):
                session.add(
                    GastoParticipante(
                        gasto_id=gasto.id,
                        miembro_id=miembro.id,
                        monto_correspondiente=parte_participante,
                    )
                )
            gastos_creados.append(gasto)

        session.commit()
        for gasto_creado in gastos_creados:
            session.refresh(gasto_creado)
            _ = gasto_creado.participantes

        for gasto_creado in gastos_creados:
            registrar_actividad(
                casa_id,
                TipoActividadEnum.GASTO_REGISTRADO,
                pagado_por,
                f"{pagador.nombre} registró un gasto de ${gasto_creado.importe} "
                f"({gasto_creado.descripcion}).",
            )

        return gastos_creados
    except (ValidationError, PermissionDeniedError, NotFoundError):
        session.rollback()
        raise
    finally:
        session.close()


def _sumar_meses(fecha: date, n: int) -> date:
    """Suma `n` meses calendario a `fecha`, ajustando el día si el mes
    destino tiene menos días que `fecha.day` (ej. 31 ene + 1 mes -> 28/29
    feb) — spec `gastos-en-cuotas`. Sin `python-dateutil` (no es una
    dependencia declarada del proyecto): solo aritmética de
    `year`/`month` y `calendar.monthrange` para acotar el día."""
    mes_total = fecha.month - 1 + n
    anio = fecha.year + mes_total // 12
    mes = mes_total % 12 + 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)


def _resolver_participantes(session, casa_id: UUID, participantes: Optional[Iterable[UUID]]):
    if participantes:
        ids_unicos = list(dict.fromkeys(participantes))
        miembros = (
            session.query(Miembro)
            .filter(Miembro.casa_id == casa_id, Miembro.id.in_(ids_unicos))
            .all()
        )
        if len(miembros) != len(ids_unicos):
            raise NotFoundError("Uno o más participantes no pertenecen a esta casa.")
        return miembros

    return (
        session.query(Miembro)
        .filter(Miembro.casa_id == casa_id, Miembro.activo.is_(True))
        .all()
    )


def _dividir_importe(importe: Decimal, cantidad: int) -> List[Decimal]:
    """Divide `importe` en `cantidad` partes iguales, ajustando el
    redondeo en la última parte para que la suma sea exactamente
    `importe` (REQ-004, TC-006)."""
    parte = (importe / cantidad).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    partes = [parte] * (cantidad - 1)
    ultima = importe - sum(partes)
    partes.append(ultima)
    return partes


def listar_gastos(casa_id: UUID):
    """Historial de gastos de una casa, ordenado por fecha descendente
    (REQ-008/TC-010). Incluye gastos pagados por miembros ya
    desactivados: no se filtra por `Miembro.activo`.

    Spec `gastos-suscripcion-mensual` (REQ-002): antes de la query
    existente, dispara la generación perezosa del gasto del mes actual
    para cada suscripción activa de la casa que todavía no lo tenga —
    el "disparador" es la primera visita del mes a esta casa (pantalla
    Gastos o Inicio, que ya llama a esta misma función), sin scheduler
    nuevo. Import diferido (no al tope del módulo) para evitar un ciclo:
    `suscripcion_service` importa `gasto_service.registrar_gasto`.
    """
    from src.services import suscripcion_service

    suscripcion_service.generar_gastos_pendientes(casa_id)

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")
        gastos = (
            session.query(Gasto)
            .filter(Gasto.casa_id == casa_id)
            .order_by(Gasto.fecha.desc())
            .all()
        )
        for gasto in gastos:
            _ = gasto.participantes
        return gastos
    finally:
        session.close()
