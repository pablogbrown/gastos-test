# T2 — Servicio de suscripciones + generación perezosa

## Scope
- `src/services/suscripcion_service.py` (nuevo).
- `src/services/gasto_service.py` — `registrar_gasto` gana `suscripcion_id`; `listar_gastos` llama a la generación perezosa.
- `tests/integration/services/suscripcion.test.py` (nuevo) — TC-001 a TC-005.

## Changes
**Service Logic**
- `gasto_service.registrar_gasto(..., suscripcion_id: Optional[UUID] = None)`:
  agregar `suscripcion_id=suscripcion_id` al `Gasto` creado — ningún otro
  cambio de comportamiento (parámetro puramente de etiquetado, igual de
  independiente que `cuotas`).
- Nuevo `suscripcion_service.py`:
  - `crear_suscripcion(casa_id, descripcion, importe, categoria_id, actor) -> Suscripcion`
    — valida igual que `registrar_gasto` (nombre, importe > 0, categoría
    existe), requiere `actor` Administrador activo (REQ-004, mismo
    criterio que `_validar_actor_admin` de `miembro_service`), crea la
    fila `Suscripcion` (`pagado_por=actor`, `activa=True`,
    `ultimo_mes_generado=None`), hace commit, y de inmediato llama a
    `gasto_service.registrar_gasto(casa_id, descripcion, importe, fecha=date.today(),
    categoria_id=categoria_id, pagado_por=actor, actor=actor,
    suscripcion_id=suscripcion.id)`, actualizando
    `ultimo_mes_generado` al mes actual tras esa llamada.
  - `listar_suscripciones(casa_id) -> List[Suscripcion]`.
  - `cancelar_suscripcion(casa_id, suscripcion_id, actor) -> Suscripcion`
    — requiere Administrador (REQ-004); setea `activa=False`; no toca
    ningún `Gasto` ya generado (REQ-003).
  - `generar_gastos_pendientes(casa_id) -> None` — para cada
    `Suscripcion` de `casa_id` con `activa=True` y
    `ultimo_mes_generado != mes_actual` (`date.today().strftime("%Y-%m")`),
    llama a `gasto_service.registrar_gasto(..., suscripcion_id=s.id)`
    con los datos de la suscripción y actualiza `ultimo_mes_generado`.
- `gasto_service.listar_gastos(casa_id)`: llamar a
  `suscripcion_service.generar_gastos_pendientes(casa_id)` como primera
  línea, antes de la query de gastos existente.

## Design Rationale
`generar_gastos_pendientes` vive en `suscripcion_service` (dueño de la
regla "qué mes le toca a esta suscripción"), pero delega en
`gasto_service.registrar_gasto` para el efecto real — evita que
`suscripcion_service` conozca cómo se reparte un gasto entre
participantes, que es responsabilidad exclusiva de `gasto_service`
(mismo principio de un-servicio-por-responsabilidad ya establecido en
el proyecto).

## Dependencies
T1 — necesita el modelo `Suscripcion` y `Gasto.suscripcion_id`.

## Done When
- [x] TC-001 a TC-005 pasan.
- [x] `pytest tests/` completo sigue en verde — en particular,
      `listar_gastos` sin ninguna suscripción activa en la casa se
      comporta exactamente igual que antes (ningún test existente de
      `gastos`/`dashboard` se rompe).

## Interfaces Produced
- `suscripcion_service.crear_suscripcion`, `listar_suscripciones`,
  `cancelar_suscripcion`, `generar_gastos_pendientes` — todas nuevas.

## Interfaces Consumed
- `Suscripcion`, `Gasto.suscripcion_id` (T1).

## Standalone Verifiable
Sí — TC-001 a TC-005 verifican el servicio directo, sin depender de las
rutas HTTP (T3) ni del frontend (T4).
