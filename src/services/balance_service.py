"""Servicio de Balance: cálculo agregado de pagos vs. montos
correspondientes (REQ-005) y sugerencia de transferencias (REQ-006).

Separado de `gasto_service` a propósito (SRP): el registro de gastos y
el cálculo agregado de balance cambian por razones distintas — nuevas
reglas de división de un gasto vs. nuevas formas de presentar el saldo
de una casa.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy import func

from src.db.base import get_session
from src.db.models.casa import Casa
from src.db.models.gasto import Gasto, GastoParticipante
from src.db.models.miembro import Miembro
from src.services.exceptions import NotFoundError


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


def calcular_balance(casa_id: UUID) -> List[BalancePorMiembro]:
    """Balance por miembro: total pagado menos total correspondiente
    (REQ-005). Incluye a todo miembro de la casa, activo o no —
    REQ-007/REQ-008 exigen que el historial y sus efectos sobrevivan a
    la desactivación de un miembro.
    """
    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        miembros = session.query(Miembro).filter(Miembro.casa_id == casa_id).all()

        pagos = dict(
            session.query(Gasto.pagado_por, func.sum(Gasto.importe))
            .filter(Gasto.casa_id == casa_id)
            .group_by(Gasto.pagado_por)
            .all()
        )
        correspondientes = dict(
            session.query(
                GastoParticipante.miembro_id, func.sum(GastoParticipante.monto_correspondiente)
            )
            .join(Gasto, Gasto.id == GastoParticipante.gasto_id)
            .filter(Gasto.casa_id == casa_id)
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
