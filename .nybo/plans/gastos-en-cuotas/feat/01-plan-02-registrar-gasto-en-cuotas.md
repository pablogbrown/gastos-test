# T2 — `registrar_gasto` genera N gastos en cuotas

## Scope
- `src/services/gasto_service.py` — `registrar_gasto`, nuevo helper `_sumar_meses`.
- `tests/integration/services/gasto_cuotas.test.py` (nuevo) — TC-001, TC-002, TC-003, TC-004, TC-005, TC-006 (esta última ejercita `registrar_gasto` + `calcular_balance` juntos — depende de que `balance-mensual` ya esté mergeada).

## Changes
**Service Logic**
- Nuevo helper (sin agregar `python-dateutil` — no es una dependencia
  declarada del proyecto):
  ```python
  import calendar

  def _sumar_meses(fecha: date, n: int) -> date:
      mes_total = fecha.month - 1 + n
      anio = fecha.year + mes_total // 12
      mes = mes_total % 12 + 1
      dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
      return date(anio, mes, dia)
  ```
- `registrar_gasto(..., cuotas: Optional[int] = None)`: si `cuotas is
  not None`, validar `cuotas >= 2` (`ValidationError` si no) ANTES de
  cualquier otra validación de negocio existente. Si `cuotas` es `None`
  o el chequeo no aplica, el resto de la función queda exactamente
  igual (REQ-003).
- Cuando `cuotas >= 2`: calcular `partes = _dividir_importe(importe_decimal,
  cuotas)` (función ya existente, reutilizada tal cual). Generar un
  `cuota_grupo_id = uuid.uuid4()` una sola vez. Por cada `i` en
  `range(cuotas)`: crear un `Gasto` con
  `descripcion=f"{descripcion.strip()} ({i+1}/{cuotas})"`,
  `importe=partes[i]`, `fecha=_sumar_meses(fecha, i)`,
  `cuota_grupo_id=cuota_grupo_id`, `cuota_numero=i+1`,
  `cuota_total=cuotas` — mismos `categoria_id`/`pagado_por` y mismos
  `GastoParticipante` (recalculando el reparto de `partes[i]` entre
  `miembros_participantes`, reutilizando `_dividir_importe` otra vez a
  nivel participante, igual que hoy). Registrar actividad
  (`GASTO_REGISTRADO`) una vez por cuota generada, mismo hook ya
  existente. La función devuelve el primer `Gasto` creado (ver
  Tradeoffs del overview).

## Design Rationale
Reutiliza `_dividir_importe` para dos niveles de reparto (entre cuotas,
y dentro de cada cuota entre participantes) en vez de escribir una
lógica de redondeo nueva — el criterio de "el ajuste va en el último"
ya está probado y es el mismo en ambos casos.

## Dependencies
T1 — necesita las columnas nuevas en `Gasto`.

## Done When
- [ ] TC-001 a TC-006 pasan.
- [ ] `pytest tests/` completo sigue en verde (incluye que un gasto sin
      `cuotas` siga comportándose exactamente igual, TC-004).

## Interfaces Produced
Ninguna nueva — `registrar_gasto` extiende su firma con un parámetro
opcional (`cuotas`), sin romper llamadores existentes.

## Standalone Verifiable
Sí — TC-001 a TC-005 verifican el servicio directamente, sin depender
de la ruta HTTP (T3) ni del frontend (T4).
