# T2 — `resumen_importer_service`; helpers de cuotas/suscripción detectada

## Scope
- `src/services/resumen_importer_service.py` (nuevo).
- `src/services/suscripcion_service.py` — nueva función.
- `src/services/gasto_service.py` — nueva función + `tarjeta_id` en `registrar_gasto`.
- `src/services/categoria_service.py` — helper find-or-create (si no existe ya un patrón equivalente).
- `tests/integration/services/resumen_importer.test.py` (nuevo).

## Changes
**`gasto_service.py`**
- `registrar_gasto(..., tarjeta_id: Optional[UUID] = None)`: persiste en `Gasto.tarjeta_id`. Sin validación adicional — `None` es válido (gasto no importado).
- `registrar_gasto_cuotas_restantes(casa_id, descripcion, importe_por_cuota, fecha_inicio, cuota_actual, cuota_total, categoria_id, pagado_por, actor, moneda, tarjeta_id) -> List[Gasto]`:
  crea `cuota_total - cuota_actual + 1` gastos (uno por mes consecutivo
  desde `fecha_inicio`, reutilizando `_sumar_meses`), cada uno con
  `importe_por_cuota` (sin dividir — ya es el monto de cada cuota),
  `cuota_numero` de `cuota_actual` a `cuota_total`, mismo
  `cuota_grupo_id` para las N filas, mismo `tarjeta_id`/`moneda`
  (TC-004).

**`suscripcion_service.py`**
- `registrar_suscripcion_detectada(casa_id, descripcion, importe, categoria_id, pagado_por, actor, moneda, fecha, tarjeta_id) -> Tuple[Suscripcion, bool]`
  (`bool` = si el actor no era Administrador y se degradó a gasto
  suelto — ver abajo):
  - Busca una `Suscripcion` activa en `casa_id` con `descripcion`
    igual (case-insensitive) — si existe, la reutiliza (TC-006).
  - Si no existe: si `actor` es Administrador de la casa, crea la
    `Suscripcion` directamente (sin pasar por `crear_suscripcion` — ver
    Design Rationale en `00-overview.md`) con
    `ultimo_mes_generado = None` (TC-005); si no es Administrador,
    **no** crea la Suscripcion — devuelve `(None, True)` para que el
    importador registre esa línea como gasto suelto (TC-007).
  - Si hay Suscripcion (nueva o existente): llama a `registrar_gasto`
    con `fecha`/`importe`/`moneda`/`tarjeta_id`/`suscripcion_id=
    suscripcion.id`, y actualiza `suscripcion.ultimo_mes_generado` al
    mes de `fecha` (evita que la generación perezosa mensual duplique
    ese mismo mes más adelante).

**`categoria_service.py`**
- `obtener_o_crear_categoria(casa_id, nombre, actor) -> Categoria`: si
  ya existe una categoría con ese nombre (case-insensitive) en la casa,
  la devuelve; si no, la crea. Usado por el importador con
  `nombre="Importado"` para todo gasto sin categoría inferible del PDF.

**`resumen_importer_service.py`**
- `importar_resumen(casa_id, tarjeta_id, pdf_bytes, actor) ->
  ResumenImportado` (dataclass `gastos_creados: int, cuotas_creadas:
  int, suscripciones_vinculadas: int, tarjeta: TarjetaCredito`):
  1. `tarjeta = tarjeta_service` — valida que `tarjeta_id` existe y
     pertenece a `casa_id` (`NotFoundError` si no).
  2. `resumen = pdf_resumen_parser.parse_resumen_bbva(pdf_bytes)` —
     `PdfFormatoNoReconocidoError` se propaga tal cual (TC-009, la ruta
     la traduce a 422).
  3. `tarjeta_service.actualizar_tarjeta(casa_id, tarjeta_id, actor,
     fecha_cierre_actual=resumen.fecha_cierre_actual,
     fecha_vencimiento_actual=resumen.fecha_vencimiento_actual,
     saldo_actual_ars=resumen.saldo_actual_ars,
     saldo_actual_usd=resumen.saldo_actual_usd)` (TC-001).
  4. `categoria = obtener_o_crear_categoria(casa_id, "Importado", actor)`.
  5. Por cada `consumo` en `resumen.consumos`:
     - `moneda = "USD" if consumo.importe_usd is not None else "ARS"`;
       `importe = consumo.importe_usd or consumo.importe_ars`.
     - Si `descripcion` matchea `SUSCRIPCIONES_RECONOCIDAS` (constante:
       `["NETFLIX", "SPOTIFY", "DISNEY"]`, substring case-insensitive) →
       `registrar_suscripcion_detectada(...)` (TC-005/TC-006/TC-007).
     - Elif `consumo.cuota_actual is not None` →
       `registrar_gasto_cuotas_restantes(...)` (TC-004).
     - Else → `registrar_gasto(..., tarjeta_id=tarjeta_id, moneda=moneda,
       pagado_por=tarjeta.miembro_id, categoria_id=categoria.id)`
       (TC-002/TC-003).
  6. Devuelve los contadores acumulados + la tarjeta actualizada.

## Design Rationale
Ver `00-overview.md` — por qué ninguna de las 2 funciones nuevas
reutiliza `crear_suscripcion`/`_crear_gastos_en_cuotas` tal cual.

## Dependencies
T1 (`pdf_resumen_parser`, `Gasto.tarjeta_id`); `tarjetas-credito`
(`tarjeta_service`); `gastos-multi-moneda` (`moneda` en `registrar_gasto`).

## Done When
- [ ] TC-001 a TC-009 pasan a nivel de servicio (sin HTTP).

## Interfaces Produced
- `importar_resumen`, `registrar_gasto_cuotas_restantes`, `registrar_suscripcion_detectada`, `obtener_o_crear_categoria`.

## Standalone Verifiable
Sí.
