# T3 — Meta de puntos mensual de la casa

## Scope
- `src/db/models/casa.py`: agregar `meta_puntos_mensual = Column(
  Integer, nullable=True)`.
- `src/services/casa_service.py`: `actualizar_meta_puntos(casa_id,
  meta: Optional[int], actor)` — requiere Administrador
  (`_validar_actor_admin`).
- `src/services/ranking_service.py` (o `casa_service.py`, el que
  tenga menos import cruzado): `calcular_progreso_meta(casa_id, mes:
  str) -> Optional[dict]` — `None` si no hay meta configurada; si la
  hay, `{puntos_acumulados, meta, porcentaje}` sumando `calcular_
  ranking(casa_id, mes)` entre todos los miembros.
- `src/services/dashboard_service.py`: `DashboardCasa` gana
  `meta_casa: Optional[dict]`, poblado por `armar_dashboard` con el
  mes actual.
- `src/api/routes/casas.py`: nuevo `PATCH /casas/{casa_id}/meta` (solo
  Administrador).
- `src/api/routes/dashboard.py`: `DashboardOut` gana `meta_casa`
  aliaseado a `metaCasa` (`[API-01]`, solo el campo contenedor).
- `src/frontend/api/casasClient.ts`: `actualizarMetaPuntos(casaId,
  meta)`.
- `src/frontend/api/dashboardClient.ts`: `DashboardCasa` (frontend)
  gana `metaCasa?: { puntosAcumulados, meta, porcentaje } | null`.

## Dependencies
T1 (`calcular_progreso_meta` reusa `calcular_ranking(casa_id, mes)`).

## Done When
- TC-006 pasa.
- Una casa sin meta configurada sigue mostrando el dashboard
  exactamente igual que hoy (`meta_casa` es `None`, no rompe ningún
  test existente de `dashboard_service`).

## Verifiability
INTEGRATION — nuevo `tests/integration/services/meta_casa.test.py`.
