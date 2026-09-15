---
feature: importar-resumen-tarjeta
schema: build-results/2
cycle: 1
updated: '2026-09-15T00:00:00Z'
exit: in-progress
verdict: pending
judgment:
  entries: 6
observations:
  entries: 0
---
### Goal

Implementar la spec `importar-resumen-tarjeta` completa: T1 parser puro
`pdf_resumen_parser` + `Gasto.tarjeta_id` + migración 0012, T2
`resumen_importer_service` (orquestación, ruteo a gasto normal/cuotas
restantes/suscripción detectada), T3 endpoint de subida de PDF, T4 botón
"Importar resumen" en la pantalla Tarjetas. Pre-requisito cumplido antes
de T1: `main` (con `gastos-multi-moneda` y `tarjetas-credito` ya
shippeadas) mergeado sin conflictos a la rama, suite completa
reverificada en verde (223 backend + 91 frontend, build/lint limpios),
merge pusheado.

### Judgment

- **J001** `Gasto.tarjeta_id` se implementó SIN `ForeignKey()` a nivel de
  modelo (mismo criterio que `suscripcion_id`/`cuota_grupo_id`), con la
  FK real agregada vía SQL crudo (`ALTER TABLE ... REFERENCES
  tarjetas_credito(id)`) en `0012_gasto_tarjeta_id.py` — el plan dejaba
  esto "a verificar al implementar". Confirmado necesario: `0002_gastos.py`
  crea la tabla `gastos` vía `create_all` ANTES de que `0011_tarjetas_
  credito.py` registre `TarjetaCredito` en `Base.metadata` durante la
  secuencia de `run_migrations` — un `ForeignKey()` a nivel de modelo
  hubiera lanzado `NoReferencedTableError` en cualquier base nueva.
- **J002** Descubierto durante la verificación de idempotencia contra
  Postgres real: en una base creada desde cero, `gastos.tarjeta_id` (igual
  que `suscripcion_id` ya hoy) termina SIN la FK real a nivel de Postgres,
  porque `0002_gastos.py`'s `create_all` ya materializa la tabla completa
  con TODAS las columnas del modelo `Gasto` vigente (incluida `tarjeta_id`)
  desde el arranque — el `ALTER TABLE ADD COLUMN IF NOT EXISTS ...
  REFERENCES` de `0012` nunca llega a ejecutarse contra una base nueva
  (la columna ya existe). La `REFERENCES` de `0012` sigue siendo correcta
  para el path real de producción (una base existente donde `gastos` ya
  existía sin `tarjeta_id` antes de este deploy). No es una regresión
  introducida por esta spec — es la misma limitación preexistente que ya
  tiene `suscripcion_id` (`0009`), documentada ahora explícitamente en el
  test de migraciones. Ver Observations/suggestions.yaml para el hallazgo
  completo.
- **J003** Parser (`pdf_resumen_parser.py`) usa `pdfplumber.extract_text
  (layout=True)` (no el modo default, que colapsa el espaciado entre
  columnas a un solo espacio) para preservar la separación real entre las
  columnas "pesos"/"dólares" de la tabla Consumos. Para decidir a qué
  columna pertenece un importe encontrado en una línea (dado que una de
  las dos columnas suele estar vacía y no deja rastro en el texto), se usa
  la línea "TOTAL CONSUMOS" —siempre trae ambos totales poblados— como
  ancla de posición de columna, clasificando cada importe de cada línea de
  consumo por cercanía a esas dos posiciones. Decisión de implementación
  dentro de la libertad explícita que daba `01-plan-01-parser-pdf.md`
  ("decisión de implementación libre siempre que TC-002/003/004/008/009
  queden cubiertos").
- **J004** `resumen_importer_service.importar_resumen` parsea el PDF
  ANTES de validar que `tarjeta_id` existe/pertenece a la casa (el plan
  listaba el orden inverso) — se fusionó la validación de existencia de
  la tarjeta con la llamada a `tarjeta_service.actualizar_tarjeta` (que
  ya la hace por su cuenta, lanzando `NotFoundError`), evitando una
  lectura separada solo para esa validación. Sin impacto en ningún TC
  (ninguno ejercita la combinación "tarjeta inexistente + PDF también mal
  formado" para distinguir qué error debería ganar). Deviation dentro de
  `spec-deviation`, settleable en L2.
- **J005** `ResumenImportado.gastos_creados` es el TOTAL de filas `Gasto`
  persistidas por la importación (incluye las de `cuotas_creadas` y las
  vinculadas a `suscripciones_vinculadas` — no una cuarta categoría
  aparte), interpretando literalmente el mensaje de T4 ("N gastos
  creados (X en cuotas, Y vinculados a suscripciones)") como "N total,
  desglosado en X e Y". `00-overview.md`/T2 no lo dejaban 100% explícito;
  T3/T4 no tienen tests que dependan de la interpretación contraria.
- **J006** T3 requirió agregar `python-multipart` a `requirements.txt`
  (necesaria para que FastAPI parsee `multipart/form-data`/`UploadFile`)
  — no estaba en `spec.md`'s `exceptions` (que solo confirmó `pdfplumber`
  con el usuario). `new-dependency` nunca es settleable en ningún trust
  level: registrada como decisión abierta no bloqueante `D001` en
  `evidence/decisions.yaml` en vez de asumirla silenciosamente — el build
  continuó (es un requisito técnico ineludible de lo que T3 ya
  especificaba), pero queda pendiente de confirmación explícita del
  humano antes de shippear.

### Observations

_Pendiente — se completa al finalizar el build._

### Verification

_Pendiente — se completa tras el pase de verify a nivel de spec (una sola
vez, al final de todas las tareas)._

### Curation

_Pendiente._
