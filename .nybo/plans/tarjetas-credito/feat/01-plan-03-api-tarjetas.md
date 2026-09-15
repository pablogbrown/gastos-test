# T3 — Rutas de tarjetas; dashboard expone alertas

## Scope
- `src/api/routes/tarjetas.py` (nuevo).
- `src/api/main.py` — registrar `tarjetas_router`.
- `src/api/routes/dashboard.py`
- `src/services/dashboard_service.py`
- `tests/integration/api/tarjetas_routes.test.py` (nuevo).

## Changes
- `tarjetas.py`: `TarjetaCreate`, `TarjetaUpdate` (todos los campos
  opcionales), `TarjetaOut`, `TarjetaAlertaOut` — mismo patrón que
  `suscripciones.py` (esquemas Pydantic en el propio archivo de ruta).
  - `POST /casas/{id}/tarjetas` → `crear_tarjeta`.
  - `GET /casas/{id}/tarjetas` → `listar_tarjetas`.
  - `PATCH /casas/{id}/tarjetas/{tarjeta_id}` → `actualizar_tarjeta`.
  - `DELETE /casas/{id}/tarjetas/{tarjeta_id}` → `eliminar_tarjeta` (204).
- `dashboard_service.DashboardCasa`: agregar campo
  `tarjetas_con_alerta: List[TarjetaAlerta] = field(default_factory=list)`;
  `armar_dashboard` llama a `obtener_tarjetas_con_alerta(casa_id)`.
- `dashboard.py`: `DashboardResponse` agrega `tarjetas_con_alerta: List[TarjetaAlertaOut]`.

## Design Rationale
Router propio `tarjetas.py` — mismo criterio que separó
`casas.py`/`gastos.py`/`tareas.py`/`suscripciones.py`/`dashboard.py`
entre sí (un recurso HTTP por módulo).

## Dependencies
T2 (`tarjeta_service`).

## Done When
- [ ] TC-001 a TC-004 pasan a nivel HTTP.
- [ ] `GET .../dashboard` incluye `tarjetas_con_alerta`.

## Interfaces Produced
- `TarjetaOut`, `TarjetaAlertaOut`.

## Interfaces Consumed
- T2: `crear_tarjeta`, `listar_tarjetas`, `actualizar_tarjeta`, `eliminar_tarjeta`, `obtener_tarjetas_con_alerta`.

## Standalone Verifiable
Sí.
