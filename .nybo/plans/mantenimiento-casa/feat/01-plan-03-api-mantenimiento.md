# T3 — Rutas; dashboard expone la alerta

## Scope
- `src/api/routes/mantenimiento.py` (nuevo).
- `src/api/main.py` — registrar el router.
- `src/services/dashboard_service.py`.
- `src/api/routes/dashboard.py`.
- `tests/integration/api/mantenimiento_routes.test.py` (nuevo).

## Changes
- `mantenimiento.py`: `ItemMantenimientoCreate {nombre, descripcion?,
  fecha_estimada?, recurrente?, periodicidad?, materiales?:
  List[{nombre, cantidad}]}`, `MaterialCreate {nombre, cantidad}`,
  `MaterialEstadoUpdate {conseguido: bool}`, `ItemMantenimientoOut`,
  `MaterialOut`, `ItemMantenimientoAlertaOut` — mismo patrón que
  `tarjetas.py` (esquemas Pydantic en el propio archivo de ruta).
  - `POST/GET /casas/{id}/mantenimiento` → `crear_item`/`listar_items`.
  - `PATCH /casas/{id}/mantenimiento/{item_id}` → `completar_item`
    (mismo contrato acotado que `TareaEstadoUpdate`: solo transición a
    "completado").
  - `POST /casas/{id}/mantenimiento/{item_id}/materiales` →
    `agregar_material`.
  - `PATCH /casas/{id}/mantenimiento/{item_id}/materiales/{material_id}`
    → `actualizar_material`.
- `dashboard_service.DashboardCasa`: agregar
  `mantenimiento_con_alerta: List[ItemMantenimientoAlerta] =
  field(default_factory=list)`; `armar_dashboard` llama a
  `obtener_items_con_alerta(casa_id)`.
- `dashboard.py`: `DashboardResponse` agrega
  `mantenimiento_con_alerta: List[ItemMantenimientoAlertaOut] =
  Field(default_factory=list, alias="mantenimientoConAlerta")` — **[API-01]**:
  el campo contenedor de nivel superior en `DashboardOut` lleva alias
  camelCase (mismo criterio que `tarjetasConAlerta`); `ItemMantenimientoAlertaOut`
  en sí queda snake_case sin alias, igual que `TarjetaAlertaOut`.

## Design Rationale
Mismo patrón que `tarjetas.py`/`prestamos.py` — router propio, un
recurso HTTP por módulo.

## Dependencies
T2 (`mantenimiento_service`).

## Done When
- [ ] TC-001 a TC-004, TC-006, TC-007 pasan a nivel HTTP.
- [ ] `GET .../dashboard` incluye `mantenimiento_con_alerta`.

## Interfaces Produced
- `ItemMantenimientoOut`, `MaterialOut`, `ItemMantenimientoAlertaOut`.

## Interfaces Consumed
- T2: todas las funciones de `mantenimiento_service`.

## Standalone Verifiable
Sí.
