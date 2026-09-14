# Solution Overview — Altas y bajas de miembro no quedan en el Historial

## File Index
- [../spec.md](../spec.md)
- [10-verify.md](10-verify.md)
- [99-progress.md](99-progress.md)

### Task Index

| Task | File | Description | Dependencies |
|---|---|---|---|
| T1 | [01-plan-01-registrar-actividad-miembro.md](01-plan-01-registrar-actividad-miembro.md) | Nuevo tipo `MIEMBRO_DESACTIVADO` + wiring de `registrar_actividad` en alta y baja de miembro | — |
| T2 | [01-plan-02-frontend-tipo-actividad.md](01-plan-02-frontend-tipo-actividad.md) | Frontend reconoce el nuevo tipo con ícono y etiqueta | T1 |

## Problema y solución
`registrar_actividad` (hook append-only) ya es el patrón establecido por
`gasto_service`/`tarea_service`: se llama una vez, después del `commit`
de la operación de negocio. `miembro_service.py` nunca adoptó ese
patrón — ni para alta (`agregar_miembro`) ni para baja
(`desactivar_miembro`) — a pesar de que el enum `MIEMBRO_AGREGADO` ya
existe, sugiriendo que se planeó y no se completó. T1 cierra ambos
lados con el mismo hook ya usado en el resto del código. T2 evita que el
frontend rompa al recibir un `tipo` que `ETIQUETAS_TIPO`/`ICONOS_TIPO`
todavía no reconocen (acceso a índice `undefined` en un `Record`
tipado).

## Arquitectura
Sin cambios — reutiliza el mismo servicio (`actividad_service.py`) y el
mismo modelo (`HistorialActividad`) ya usados por `gasto_service`/
`tarea_service`.

## Data Model
Un nuevo valor en el enum de Python `TipoActividadEnum` (columna
`Enum(TipoActividadEnum)` en Postgres) — no requiere migración de
esquema porque SQLAlchemy/Postgres aceptan el nuevo valor del enum
Python sin cambiar el tipo de columna subyacente (es un `Enum` nativo de
Postgres creado a partir del enum de Python; agregar un valor nuevo al
enum de Python y reiniciar la app basta, sin `ALTER TYPE`, ya que el
enum de Postgres se recrea desde cero solo en un entorno sin datos —
para producción esto se documenta como Open Item en Tradeoffs).

## Tradeoffs
- **Agregar valor a un enum nativo de Postgres en producción** requiere
  típicamente `ALTER TYPE ... ADD VALUE` fuera de una transacción — este
  fix no incluye una migración explícita para eso porque el entorno de
  este proyecto recrea el esquema en cada `migrate` (ver
  `dockerize-local-env`); queda documentado acá para quien opere un
  entorno con datos ya persistidos.

## API/Data Contracts
- `GET /casas/{casa_id}/actividad`: sin cambio de forma — el `tipo` del
  `ActividadOut` ya es `str`; solo se agrega un valor nuevo posible.
- Frontend `Actividad["tipo"]` (dashboardClient.ts): agrega
  `"miembro_desactivado"` a la unión de tipos ya existente.
