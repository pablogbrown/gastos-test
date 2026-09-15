# T1 — `calcular_balance` filtra por mes

## Scope
- `src/services/balance_service.py` — `calcular_balance`, nuevo helper `_rango_mes`.
- `tests/integration/services/balance_mensual.test.py` (nuevo) — TC-001, TC-002, TC-003 (a nivel servicio; TC-003 también se re-verifica a nivel HTTP en T2).

## Changes
**Service Logic**
- Nuevo helper:
  ```python
  def _rango_mes(mes: Optional[str]) -> tuple[date, date]:
      if mes is None:
          hoy = date.today()
          anio, numero_mes = hoy.year, hoy.month
      else:
          try:
              anio, numero_mes = (int(p) for p in mes.split("-"))
              if not (1 <= numero_mes <= 12):
                  raise ValueError
          except ValueError as exc:
              raise ValidationError(f"Formato de mes inválido: {mes!r}. Se espera 'YYYY-MM'.") from exc
      ultimo_dia = calendar.monthrange(anio, numero_mes)[1]
      return date(anio, numero_mes, 1), date(anio, numero_mes, ultimo_dia)
  ```
- `calcular_balance(casa_id: UUID, mes: Optional[str] = None)`: resolver
  `desde, hasta = _rango_mes(mes)` y agregar
  `.filter(Gasto.fecha.between(desde, hasta))` a ambas queries de
  agregación (`pagos` y `correspondientes`) — mismo filtro en las dos,
  para que "pagó" y "le correspondía" sigan siendo comparables dentro
  del mismo mes.

## Design Rationale
El filtro se resuelve una sola vez (`_rango_mes`) y se aplica igual a
ambas queries — evita que un cambio futuro filtre un lado sí y el otro
no, que rompería silenciosamente la resta `pago - correspondía`.

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] TC-001, TC-002, TC-003 pasan (TC-003 a nivel de excepción de servicio acá; T2 la re-verifica como 400 HTTP).
- [ ] `pytest tests/` completo sigue en verde.

## Interfaces Produced
- `calcular_balance` — firma extendida: `{name: "calcular_balance", signature: "(casa_id: UUID, mes: Optional[str] = None) -> List[BalancePorMiembro]", kind: "function"}` (mismo nombre, parámetro nuevo con default — llamadas existentes sin `mes` siguen compilando).

## Standalone Verifiable
Sí.
