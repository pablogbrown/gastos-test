# Overview: resumen-tarjeta-pago

## Data Model

Nueva tabla `resumenes_tarjeta` (modelo `ResumenTarjeta`,
`src/db/models/resumen_tarjeta.py`):

```python
id = Column(GUID(), primary_key=True, default=uuid.uuid4)
casa_id = Column(GUID(), ForeignKey("casas.id"), nullable=False)
tarjeta_id = Column(GUID(), ForeignKey("tarjetas_credito.id"), nullable=False)
fecha_cierre = Column(Date, nullable=False)
fecha_vencimiento = Column(Date, nullable=False)
saldo_ars = Column(Numeric(12, 2), nullable=True)
saldo_usd = Column(Numeric(12, 2), nullable=True)
gastos_creados = Column(Integer, nullable=False, default=0)
estado = Column(String, nullable=False, default="pendiente")  # "pendiente" | "pagado"
importado_en = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
```

`tarjeta_id` usa `ForeignKey()` real a nivel de modelo — a diferencia de
`Gasto.tarjeta_id`/`Gasto.suscripcion_id`, acá es seguro: `tarjetas_
credito` ya existe desde la migración `0011`, muy anterior a la nueva
migración `0019` que crea esta tabla, así que `Base.metadata` ya la
tiene registrada quando esta tabla se declara.

`Gasto.resumen_id` (nullable, **sin** `ForeignKey()` a nivel de modelo
— mismo criterio ya documentado en `Gasto.suscripcion_id`/`Gasto.
tarjeta_id`: `gastos` se crea en la migración `0002`, mucho antes que
`resumenes_tarjeta` (`0019`); un `ForeignKey()` de SQLAlchemy exigiría
que la tabla referenciada ya esté en `Base.metadata` en ese momento, y
no lo está). La integridad referencial real la agrega `0019_resumen_
tarjeta.py` vía `ALTER TABLE gastos ADD COLUMN IF NOT EXISTS resumen_id
CHAR(36) REFERENCES resumenes_tarjeta(id)` (SQL crudo), después de crear
`resumenes_tarjeta` en esa misma migración.

## Migration `0019_resumen_tarjeta`

Una sola migración (ambas tablas relacionadas, mismo criterio que
`0018_mantenimiento_autos` con `auto_id`):

1. `resumenes_tarjeta.__table__.create(bind, checkfirst=True)` (FK real
   a `tarjetas_credito` ya resuelta por metadata).
2. SQL crudo: `ALTER TABLE gastos ADD COLUMN IF NOT EXISTS resumen_id
   CHAR(36) REFERENCES resumenes_tarjeta(id)`.

Agregar `"0019_resumen_tarjeta"` a `_MIGRACIONES` en `src/db/migrate.py`.

## Service Layer

`src/services/resumen_importer_service.py` (extendido):

- **Naming**: el dataclass existente `ResumenImportado` (resultado en
  memoria de `importar_resumen`, no persistido) se mantiene sin
  cambios de nombre — no colisiona con el nuevo modelo persistido
  `ResumenTarjeta`, que tiene su propio nombre. Se le agrega el campo
  `resumen_id: UUID` al dataclass para que el caller (API) pueda
  referenciar el registro recién creado.
- `importar_resumen(casa_id, tarjeta_id, pdf_bytes, actor)`:
  1. Parsear el PDF (sin cambios).
  2. **Nuevo — chequeo de duplicado**: buscar un `ResumenTarjeta` con
     `(tarjeta_id, fecha_cierre=resumen.fecha_cierre_actual)`. Si
     existe, `raise ConflictError(...)` **antes** de tocar la tarjeta o
     crear cualquier gasto (atómico).
  3. Actualizar la tarjeta (sin cambios).
  4. **Nuevo**: crear el `ResumenTarjeta` (estado `"pendiente"`,
     `gastos_creados=0` provisorio, saldos del resumen parseado).
  5. Igual que hoy, recorrer los consumos — pasando `resumen_id=
     resumen_registro.id` a cada mecanismo de creación de gasto.
  6. Actualizar `resumen_registro.gastos_creados` con el total final.
  7. Devolver `ResumenImportado` (dataclass) incluyendo `resumen_id`.
- **Nuevo** `pagar_resumen(casa_id, resumen_id, actor) -> ResumenTarjeta`:
  valida que el resumen exista en esa casa y no esté ya pagado
  (`ConflictError` si ya está `"pagado"`); actualiza todos los `Gasto`
  con `resumen_id=resumen_id` a `estado="pagado"` (bulk update);
  actualiza el propio resumen a `estado="pagado"`.
- **Nuevo** `listar_resumenes(casa_id, tarjeta_id) -> List[ResumenTarjeta]`:
  todos los resúmenes de esa tarjeta, más recientes primero.

`gasto_service.registrar_gasto` y `registrar_gasto_cuotas_restantes`
ganan un parámetro `resumen_id: Optional[UUID] = None`, poblando la
columna homónima en cada `Gasto` creado — mismo patrón ya usado para
`tarjeta_id`.

`suscripcion_service.registrar_suscripcion_detectada` gana el mismo
parámetro `resumen_id: Optional[UUID] = None`, threaded a su llamada
interna a `registrar_gasto`.

## API (`src/api/routes/tarjetas.py`)

- `ResumenTarjetaOut`: `id, tarjeta_id, fecha_cierre, fecha_
  vencimiento, saldo_ars, saldo_usd, gastos_creados, estado,
  importado_en`.
- `ResumenImportadoOut` gana el campo `resumen_id: UUID`.
- Nuevo `GET /casas/{casa_id}/tarjetas/{tarjeta_id}/resumenes` →
  `listar_resumenes`.
- Nuevo `PATCH /casas/{casa_id}/tarjetas/{tarjeta_id}/resumenes/
  {resumen_id}/pagar` → `pagar_resumen`.
- `importar_resumen_endpoint` agrega el mapeo `ConflictError` → 409
  (mismo criterio ya usado en `tareas.py`/`mantenimiento.py`).

## Frontend (`src/frontend/pages/Tarjetas.tsx`)

- `tarjetasClient.ts`: nuevo tipo `Resumen` (mismos campos que
  `ResumenTarjetaOut`, camelCase); `listarResumenes(casaId, tarjetaId)`
  y `pagarResumen(casaId, tarjetaId, resumenId)`; `ResumenImportado`
  gana `resumenId`.
- Cada card de tarjeta muestra una sub-lista "Resúmenes importados"
  (fecha de cierre, estado como `Chip`, botón "Pagar resumen" cuando
  `estado === "pendiente"`) — se recarga tras una importación exitosa y
  tras pagar.
- El error 409 de una importación duplicada ya se muestra de forma
  legible vía `formatErrorDetail` (sin cambios necesarios ahí — el
  `detail` de un `ConflictError` ya es un string).

## Tradeoffs
- `pagar_resumen` es todo-o-nada (no pago parcial) — consistente con
  el pedido explícito del usuario ("todos los gastos del resumen pasen
  a pagado").
- El chequeo de duplicado usa `(tarjeta_id, fecha_cierre)` como clave
  natural — dos resúmenes de la misma tarjeta nunca comparten fecha de
  cierre en la práctica (un ciclo de facturación por mes).
