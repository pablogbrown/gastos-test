# T1 — Niveles, rachas y ranking por mes

## Scope
`src/services/ranking_service.py`:
- Constante `NIVELES` y función `_nivel_de(puntos_totales: int) -> str`
  (ver shape exacto en `00-overview.md`).
- Nueva `calcular_racha(casa_id, miembro_id) -> int`: días
  consecutivos (calendario, UTC) con al menos un `HistorialTarea` de
  ese miembro, contando hacia atrás desde hoy o ayer.
- `calcular_ranking(casa_id, mes: Optional[str] = None)`: agregar el
  filtro opcional de mes (rango propio, no importar `_rango_mes` de
  `gasto_service.py`); cada entrada del resultado gana `nivel` (sobre
  el total histórico, sin filtrar por mes) y `racha`.
- `src/api/routes/tareas.py` (o donde viva la ruta de ranking): el
  endpoint de ranking acepta un query param opcional `mes`.
- `src/frontend/api/tareasClient.ts`: `RankingEntry` gana `nivel:
  string`/`racha: number`; `obtenerRanking(casaId, mes?: string)`.

## Dependencies
Ninguna (task raíz).

## Done When
- TC-001 a TC-004 pasan.
- `dashboard_service.armar_dashboard` (que llama a `calcular_ranking`
  sin `mes`) sigue devolviendo exactamente el mismo shape que hoy en
  sus tests existentes — ninguno se modifica.

## Verifiability
INTEGRATION — nuevo `tests/integration/services/gamificacion_ranking.test.py`.
Regression gate: sí (toca `ranking_service.py`, consumido por
`dashboard_service` ya cubierto por su propia suite).
