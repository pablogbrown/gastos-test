"""Servicio de Balance: total gastado por la casa y aporte informativo
por miembro (spec `gastos-sin-reparto`, REQ-003/REQ-004).

Separado de `gasto_service` a propósito (SRP): el registro de gastos y
el cálculo agregado de balance cambian por razones distintas — nuevas
reglas de registro de un gasto vs. nuevas formas de presentar el estado
de la casa.

Spec `gastos-sin-reparto`: un gasto ya no se reparte entre participantes
ni genera ninguna deuda individual — `calcular_balance` ya NO depende de
`GastoParticipante` (eliminado del sistema) ni expone ningún campo de
deuda o transferencia. `sugerir_transferencias`/`Transferencia`/
`BalancePorMiembro` se eliminan por completo: sin reparto no hay ninguna
deuda entre miembros que sugerir saldar (esa noción pasa a vivir,
conceptualmente, en la spec separada `prestamos-entre-miembros`, un
registro explícito, no un cálculo derivado).
"""
import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.gasto import Gasto
from src.db.models.miembro import Miembro
from src.services.exceptions import NotFoundError, ValidationError


@dataclass
class TotalCasaPorMoneda:
    """Total gastado por la casa en una moneda dada, en el mes
    consultado (REQ-003)."""

    moneda: str
    total_gastos: Decimal


@dataclass
class AportePorMiembro:
    """Cuánto pagó un miembro en una moneda dada, en el mes consultado
    (REQ-004) — puramente informativo, nunca una deuda ni una cifra de
    "correspondía"."""

    miembro_id: UUID
    nombre: str
    total: Decimal
    moneda: str = "ARS"


@dataclass
class BalanceCasa:
    """Resultado de `calcular_balance`: el total de la casa por moneda
    más el aporte informativo de cada miembro — sin ningún campo de
    deuda ni transferencia sugerida (REQ-003/REQ-004)."""

    totales: List[TotalCasaPorMoneda]
    aportes: List[AportePorMiembro]


def _rango_mes(mes: Optional[str]) -> Tuple[date, date]:
    """Resuelve `mes` (`YYYY-MM`, o `None` para el mes calendario actual)
    al primer y último día de ese mes (spec `balance-mensual`, REQ-001/
    REQ-002/REQ-003)."""
    if mes is None:
        hoy = date.today()
        anio, numero_mes = hoy.year, hoy.month
    else:
        try:
            anio, numero_mes = (int(parte) for parte in mes.split("-"))
            if not (1 <= numero_mes <= 12):
                raise ValueError
        except ValueError as exc:
            raise ValidationError(f"Formato de mes inválido: {mes!r}. Se espera 'YYYY-MM'.") from exc
    ultimo_dia = calendar.monthrange(anio, numero_mes)[1]
    return date(anio, numero_mes, 1), date(anio, numero_mes, ultimo_dia)


def calcular_balance(casa_id: UUID, mes: Optional[str] = None) -> BalanceCasa:
    """Balance de la casa: total gastado por moneda (REQ-003) más el
    aporte informativo de cada miembro (REQ-004), filtrado por mes — sin
    `mes`, usa el mes calendario actual (spec `balance-mensual`).

    Spec `gastos-sin-reparto`: ya NO depende de `GastoParticipante` (T1
    la eliminó por completo) ni calcula ninguna cifra de deuda —
    `pagado_por` es la única fuente de `aportes`, puramente informativa
    (REQ-005). Incluye a todo miembro de la casa, activo o no — mismo
    criterio ya establecido (el historial sobrevive a la desactivación
    de un miembro).

    Mismo criterio de separación por moneda ya existente (spec
    `gastos-multi-moneda`, nunca sumado ni convertido): para `"ARS"` se
    emite siempre una fila por cada miembro/una fila de total, incluso en
    0; para cualquier otra moneda (hoy solo `"USD"`), solo si hubo
    actividad real ese mes.
    """
    desde, hasta = _rango_mes(mes)

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        miembros = session.query(Miembro).filter(Miembro.casa_id == casa_id).all()
        nombres_por_id = {miembro.id: miembro.nombre for miembro in miembros}

        totales_por_moneda = {
            moneda: Decimal(total)
            for moneda, total in (
                session.query(Gasto.moneda, func.sum(Gasto.importe))
                .filter(Gasto.casa_id == casa_id)
                .filter(Gasto.fecha.between(desde, hasta))
                .group_by(Gasto.moneda)
                .all()
            )
        }
        aportes_por_clave = {
            (miembro_id, moneda): Decimal(total)
            for miembro_id, moneda, total in (
                session.query(Gasto.pagado_por, Gasto.moneda, func.sum(Gasto.importe))
                .filter(Gasto.casa_id == casa_id)
                .filter(Gasto.fecha.between(desde, hasta))
                .group_by(Gasto.pagado_por, Gasto.moneda)
                .all()
            )
        }

        # "ARS": siempre una fila de total (incluso en 0) — mismo
        # criterio que ya regía para `BalancePorMiembro` antes de esta
        # spec, ahora aplicado al total de la casa.
        totales: List[TotalCasaPorMoneda] = [
            TotalCasaPorMoneda(moneda="ARS", total_gastos=totales_por_moneda.get("ARS") or Decimal(0))
        ]
        for moneda in sorted(m for m in totales_por_moneda if m != "ARS"):
            totales.append(TotalCasaPorMoneda(moneda=moneda, total_gastos=totales_por_moneda[moneda]))

        # "ARS": una fila por cada miembro de la casa, incluso en 0
        # (mismo criterio preexistente). Cualquier otra moneda con
        # actividad real: una fila solo para los miembros involucrados.
        aportes: List[AportePorMiembro] = []
        for miembro in miembros:
            aportes.append(
                AportePorMiembro(
                    miembro_id=miembro.id,
                    nombre=miembro.nombre,
                    total=aportes_por_clave.get((miembro.id, "ARS")) or Decimal(0),
                    moneda="ARS",
                )
            )

        claves_no_ars = sorted(
            (clave for clave in aportes_por_clave if clave[1] != "ARS"),
            key=lambda clave: (clave[1], str(clave[0])),
        )
        for miembro_id, moneda in claves_no_ars:
            aportes.append(
                AportePorMiembro(
                    miembro_id=miembro_id,
                    nombre=nombres_por_id.get(miembro_id, str(miembro_id)),
                    total=aportes_por_clave[(miembro_id, moneda)],
                    moneda=moneda,
                )
            )

        return BalanceCasa(totales=totales, aportes=aportes)
    finally:
        session.close()
