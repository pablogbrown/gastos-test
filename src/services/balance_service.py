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
    # Spec `gastos-multi-moneda`, REQ-002: `calcular_balance` ahora
    # agrupa por (miembro, moneda) — cada fila lleva su propia moneda,
    # nunca sumadas ni convertidas entre sí.
    moneda: str = "ARS"


@dataclass
class Transferencia:
    deudor_id: UUID
    acreedor_id: UUID
    monto: Decimal
    # Spec `gastos-multi-moneda`, REQ-003: la moneda del grupo dentro del
    # que `sugerir_transferencias` emparejó este deudor con este acreedor
    # — nunca mezclada entre grupos.
    moneda: str = "ARS"


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

    Spec `gastos-multi-moneda` (REQ-002): agrupa por `(miembro, moneda)`
    en vez de solo por miembro — nunca suma ni convierte entre monedas.
    Para `"ARS"` se mantiene el comportamiento actual sin cambios: una
    fila por cada miembro de la casa, incluso en 0 (TC-004, control).
    Para cualquier otra moneda con actividad ese mes (hoy solo `"USD"`),
    se emite una fila únicamente para los miembros con pago o
    correspondencia distinta de cero en esa moneda — nunca una fila en 0
    para toda la casa (TC-004).
    """
    desde, hasta = _rango_mes(mes)

    session = get_session()
    try:
        if session.get(Casa, casa_id) is None:
            raise NotFoundError(f"La casa {casa_id} no existe.")

        miembros = session.query(Miembro).filter(Miembro.casa_id == casa_id).all()

        pagos = {
            (miembro_id, moneda): total
            for miembro_id, moneda, total in (
                session.query(Gasto.pagado_por, Gasto.moneda, func.sum(Gasto.importe))
                .filter(Gasto.casa_id == casa_id)
                .filter(Gasto.fecha.between(desde, hasta))
                .group_by(Gasto.pagado_por, Gasto.moneda)
                .all()
            )
        }
        correspondientes = {
            (miembro_id, moneda): total
            for miembro_id, moneda, total in (
                session.query(
                    GastoParticipante.miembro_id,
                    Gasto.moneda,
                    func.sum(GastoParticipante.monto_correspondiente),
                )
                .join(Gasto, Gasto.id == GastoParticipante.gasto_id)
                .filter(Gasto.casa_id == casa_id)
                .filter(Gasto.fecha.between(desde, hasta))
                .group_by(GastoParticipante.miembro_id, Gasto.moneda)
                .all()
            )
        }

        resultado: List[BalancePorMiembro] = []

        # "ARS": comportamiento actual sin cambios — una fila por cada
        # miembro de la casa, incluso en 0.
        for miembro in miembros:
            pago = Decimal(pagos.get((miembro.id, "ARS")) or 0)
            correspondia = Decimal(correspondientes.get((miembro.id, "ARS")) or 0)
            resultado.append(
                BalancePorMiembro(
                    miembro_id=miembro.id,
                    nombre=miembro.nombre,
                    pago=pago,
                    correspondia=correspondia,
                    balance=pago - correspondia,
                    moneda="ARS",
                )
            )

        # Cualquier otra moneda con actividad real este mes: una fila solo
        # para los miembros involucrados — nunca una sección vacía.
        nombres_por_id = {miembro.id: miembro.nombre for miembro in miembros}
        claves_no_ars = sorted(
            (clave for clave in set(pagos) | set(correspondientes) if clave[1] != "ARS"),
            key=lambda clave: (clave[1], str(clave[0])),
        )
        for miembro_id, moneda in claves_no_ars:
            pago = Decimal(pagos.get((miembro_id, moneda)) or 0)
            correspondia = Decimal(correspondientes.get((miembro_id, moneda)) or 0)
            resultado.append(
                BalancePorMiembro(
                    miembro_id=miembro_id,
                    nombre=nombres_por_id.get(miembro_id, str(miembro_id)),
                    pago=pago,
                    correspondia=correspondia,
                    balance=pago - correspondia,
                    moneda=moneda,
                )
            )

        return resultado
    finally:
        session.close()


def sugerir_transferencias(balance: List[BalancePorMiembro]) -> List[Transferencia]:
    """Algoritmo greedy (REQ-006): empareja al mayor deudor con el mayor
    acreedor hasta saldar todas las cuentas. No optimiza el número
    mínimo de transferencias — asunción documentada en la spec.

    Spec `gastos-multi-moneda` (REQ-003): `balance` es la lista plana
    multi-moneda de `calcular_balance` — se agrupa internamente por
    `moneda` y el algoritmo greedy corre por separado dentro de cada
    grupo, nunca emparejando un deudor de una moneda con un acreedor de
    otra. Cada `Transferencia` resultante lleva la `moneda` de su grupo.
    """
    grupos: dict = {}
    for fila in balance:
        grupos.setdefault(fila.moneda, []).append(fila)

    transferencias: List[Transferencia] = []
    for moneda in sorted(grupos):
        transferencias.extend(_sugerir_transferencias_de_una_moneda(grupos[moneda], moneda))
    return transferencias


def _sugerir_transferencias_de_una_moneda(
    balance: List[BalancePorMiembro], moneda: str
) -> List[Transferencia]:
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
                Transferencia(
                    deudor_id=deudor_id, acreedor_id=acreedor_id, monto=monto, moneda=moneda
                )
            )
        deudas[i][1] -= monto
        creditos[j][1] -= monto
        if deudas[i][1] <= 0:
            i += 1
        if creditos[j][1] <= 0:
            j += 1
    return transferencias
