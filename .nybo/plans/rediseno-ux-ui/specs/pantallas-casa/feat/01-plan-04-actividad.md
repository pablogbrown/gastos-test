# T4 — Actividad como feed cronológico

## Scope
- `src/frontend/pages/HistorialActividad.tsx`

## Changes
- Encabezado vía `PageHeader`.
- El historial se reconstruye como un `Timeline`/lista vertical con un ícono por tipo de evento (mapa centralizado `id de tipo -> ícono`, mismo patrón que `NOMBRES_LOGRO`/`FRONP-03`): alta/baja de miembro, gasto registrado, tarea completada, préstamo, mantenimiento, etc.
- Nombres de miembro/tarea resueltos por id (convención `FRON-01` ya establecida, `nombreDe` helper) — sin cambio de esa lógica.
- Sin actividad → `EmptyState`.

## Implementation Steps
1. Baseline: confirmar `HistorialActividad.test.tsx` en verde.
2. Reemplazar encabezado por `PageHeader`.
3. Definir el mapa `tipo de evento -> ícono`.
4. Reconstruir el historial como feed vertical con ícono por evento.
5. Agregar `EmptyState` si no hay actividad.
6. Re-correr el suite sin modificar queries.

## Design Rationale
Un feed cronológico con íconos es el patrón estándar para historiales de actividad (reconocible, escaneable) — reemplaza una tabla homogénea donde todos los eventos se ven iguales.

## Dependencies
Ninguna dentro de esta spec.

## Done When
- [ ] TC-006, TC-007 pasan.
- [ ] `HistorialActividad.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí.
