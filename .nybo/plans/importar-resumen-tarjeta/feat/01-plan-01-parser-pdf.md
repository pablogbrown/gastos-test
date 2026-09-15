# T1 — `pdf_resumen_parser` (puro); `Gasto.tarjeta_id`; dependencia `pdfplumber`

## Scope
- `requirements.txt` — agregar `pdfplumber`.
- `src/services/pdf_resumen_parser.py` (nuevo).
- `src/db/models/gasto.py` — 1 columna nueva.
- `src/db/migrations/0012_gasto_tarjeta_id.py` (nuevo).
- `src/db/migrate.py` — agregar `0012` a `_MIGRACIONES`.
- `tests/unit/services/pdf_resumen_parser.test.py` (nuevo) — usa un PDF
  de fixture generado o el mismo formato de muestra (sin datos
  personales reales; construir un PDF de prueba mínimo con
  `reportlab`/texto plano equivalente, o fijar el parser sobre texto ya
  extraído si generar un PDF de test resulta más costoso que necesario
  — decisión de implementación libre siempre que TC-002/003/004/008/009
  queden cubiertos).

## Changes
**Dependencia**
- `requirements.txt`: agregar `pdfplumber>=0.11,<1.0` (confirmado con el usuario).

**Parser puro (`pdf_resumen_parser.py`)**
- `parse_resumen_bbva(pdf_bytes: bytes) -> ResumenParseado`:
  - Extrae texto con `pdfplumber.open(io.BytesIO(pdf_bytes))`.
  - Busca las líneas "CIERRE ACTUAL", "VENCIMIENTO ACTUAL", "SALDO
    ACTUAL $", "SALDO ACTUAL U$S" (formato `DD-Mmm-AA`/montos con `.`
    de miles y `,` decimal, estilo AR) → `fecha_cierre_actual`,
    `fecha_vencimiento_actual`, `saldo_actual_ars`, `saldo_actual_usd`
    (`Optional[Decimal]`, `None` si la línea no aparece).
  - Si no encuentra los 2 marcadores de fecha esperados → `raise
    PdfFormatoNoReconocidoError` (nueva excepción en
    `src/services/exceptions.py`) — TC-009, nunca devuelve un resultado
    parcial.
  - Localiza la sección que empieza en una línea que matchea `^Consumos
    ` y termina en la primera línea que matchea `^TOTAL CONSUMOS` o
    `^Impuestos, cargos e intereses` (lo que aparezca primero) — todo lo
    que esté fuera de ese rango se ignora (TC-008: nunca llega a
    parsearse una línea de "Impuestos, cargos e intereses").
  - Cada línea de consumo matchea el patrón `FECHA DESCRIPCION
    [C.NN/NN] [CUPON] [IMPORTE_ARS] [IMPORTE_USD]` (columnas separadas
    por espacios múltiples, como en el PDF de muestra) →
    `ConsumoParseado(fecha: date, descripcion: str, cuota_actual:
    Optional[int], cuota_total: Optional[int], importe_ars:
    Optional[Decimal], importe_usd: Optional[Decimal])`. El patrón
    `C.NN/NN` dentro de la descripción se extrae a
    `cuota_actual`/`cuota_total` y se quita de la descripción guardada.

**Data Layer**
- `Gasto`: agregar `tarjeta_id = Column(GUID(), nullable=True)` (sin
  `ForeignKey()` a nivel de modelo salvo que, al implementar, se
  confirme que `tarjetas_credito` ya está en `Base.metadata` en el
  orden de migraciones — mismo criterio de `cuota_grupo_id`/
  `suscripcion_id`).
- Migración `0012_gasto_tarjeta_id.py`: `ALTER TABLE gastos ADD COLUMN
  IF NOT EXISTS tarjeta_id UUID` (+ `REFERENCES tarjetas_credito(id)`
  vía SQL crudo si el orden de migraciones lo permite).
- Registrar `0012` en `_MIGRACIONES` (verificar el próximo número libre
  al implementar).

## Design Rationale
Parser sin ninguna dependencia de DB ni de otros servicios — se puede
testear con un PDF/texto de fixture sin tocar Postgres, igual que
cualquier función pura del proyecto.

## Dependencies
Ninguna directa de esta feature — pero requiere que
`tarjetas-credito` (tabla `tarjetas_credito`) ya esté mergeada si se
quiere la `ForeignKey()` real; si se construye antes, usar columna
plana sin FK (mismo patrón ya usado 2 veces en este modelo).

## Done When
- [ ] TC-001, TC-002, TC-003, TC-004 (datos), TC-008, TC-009 cubiertos a nivel de parser.
- [ ] Migración corre limpia e idempotente contra Postgres real.

## Interfaces Produced
- `parse_resumen_bbva(pdf_bytes: bytes) -> ResumenParseado`.
- `ResumenParseado`, `ConsumoParseado` (dataclasses).
- `PdfFormatoNoReconocidoError`.
- `Gasto.tarjeta_id`.

## Standalone Verifiable
Sí.
