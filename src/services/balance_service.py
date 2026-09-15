"""Servicio de Balance: cálculo agregado de pagos vs. montos
correspondientes (REQ-005) y sugerencia de transferencias (REQ-006).

Separado de `gasto_service` a propósito (SRP): el registro de gastos y
el cálculo agregado de balance cambian por razones distintas — nuevas
reglas de división de un gasto vs. nuevas formas de presentar el saldo
de una casa.
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
from src.db.models.gasto import Gasto, GastoParticipante
from src.db.models.miembro import Miembro
from src.services.exceptions import NotFoundError, ValidationError


@dataclass
class BalancePorMiembro:
    miembro_id: UUID
    nombre: str
    pago: Decimal
    correspondia: Decimal
    balance: Decimal


@dataclass
class Transferencia:
    deudor_id: UUID
    acreedor_id: UUID
    monto: Decimal


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


def calcular_balance(casa_id: UUID, mes: Optional[str] = None) -> List[BalancePorMiembro]:
    """Balance por miembro: total pagado menos total correspondiente
    (REQ-005), filtrado por mes (spec `balance-mensual`, REQ-001/REQ-002)
    — sin `mes`, usa el mes calendario actual. Incluye a todo miembro de
    la casa, activo o no — REQ-007/REQ-008 exigen que el historial y sus
    efectos sobrevivan a la desactivación de un miembro.
    """
    desde, hasta = _rango_mes(mes)

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        miembros = session.query(Miembro).filter(Miembro.casa_id == casa_id).all()

        pagos = dict(
            session.query(Gasto.pagado_por, func.sum(Gasto.importe))
            .filter(Gasto.casa_id == casa_id)
            .filter(Gasto.fecha.between(desde, hasta))
            .group_by(Gasto.pagado_por)
            .all()
        )
        correspondientes = dict(
            session.query(
                GastoParticipante.miembro_id, func.sum(GastoParticipante.monto_correspondiente)
            )
            .join(Gasto, Gasto.id == GastoParticipante.gasto_id)
            .filter(Gasto.casa_id == casa_id)
            .filter(Gasto.fecha.between(desde, hasta))
            .group_by(GastoParticipante.miembro_id)
            .all()
        )

        resultado = []
        for miembro in miembros:
            pago = Decimal(pagos.get(miembro.id) or 0)
            correspondia = Decimal(correspondientes.get(miembro.id) or 0)
            resultado.append(
                BalancePorMiembro(
                    miembro_id=miembro.id,
                    nombre=miembro.nombre,
                    pago=pago,
                    correspondia=correspondia,
                    balance=pago - correspondia,
                )
            )
        return resultado
    finally:
        session.close()


def sugerir_transferencias(balance: List[BalancePorMiembro]) -> List[Transferencia]:
    """Algoritmo greedy (REQ-006): empareja al mayor deudor con el mayor
    acreedor hasta saldar todas las cuentas. No optimiza el número
    mínimo de transferencias — asunción documentada en la spec.
    """
    deudores = sorted((b for b in balance if b.balance < 0), key=lambda b: b.balance)
    acreedores = sorted((b for b in balance if b.balance > 0), key=lambda b: -b.balance)

    deudas = [[d.miembro_id, -d.balance] for d in deudores]
    creditos = [[c.miembro_id, c.balance] for c in acreedores]

    transferencias: List[Transferencia] = []
    i, j = 0, 0
    while i < len(deudas) and j < len(creditos):
        deudor_id, monto_deuda = deudas[i]
        acreedor_id, monto_credito = creditos[j]
        monto = min(monto_deuda, monto_credito)
        if monto > 0:
            transferencias.append(
                Transferencia(deudor_id=deudor_id, acreedor_id=acreedor_id, monto=monto)
            )
        deudas[i][1] -= monto
        creditos[j][1] -= monto
        if deudas[i][1] <= 0:
            i += 1
        if creditos[j][1] <= 0:
            j += 1
    return transferencias
