# T2 — Tarjetas + Suscripciones

## Scope
- `src/frontend/pages/Tarjetas.tsx`
- `src/frontend/pages/Suscripciones.tsx`

## Changes
- Encabezado de ambas vía `PageHeader` (acciones "Nueva tarjeta"/"Nueva suscripción").
- Tarjetas: cada tarjeta de crédito como `Card` con banda de alerta visual (vencimiento próximo) preservada, y lista de resúmenes importados restyled como tarjetas de línea.
- Suscripciones: lista de suscripciones activas/canceladas como tarjetas de línea con chip de estado.
- Sin tarjetas/sin suscripciones → `EmptyState`.

## Implementation Steps
1. Baseline: confirmar `Tarjetas.test.tsx`/`Suscripciones.test.tsx` en verde.
2. Reemplazar encabezados por `PageHeader`.
3. Reconstruir tarjetas de crédito y resúmenes como `Card`/tarjetas de línea, preservando la banda de alerta de vencimiento.
4. Reconstruir la lista de suscripciones con chip de estado.
5. Agregar `EmptyState` donde corresponda.
6. Re-correr ambos suites sin modificar queries.

## Design Rationale
Tarjetas y Suscripciones comparten el mismo patrón (entidad con estado activo/inactivo + acción de alta) y ambas dependen de "Nueva tarjeta"/"Nueva suscripción" como flujo primario — agruparlas mantiene el task cohesivo sin duplicar la receta de chip+card en tasks separados.

## Dependencies
Ninguna dentro de esta spec.

## Done When
- [ ] TC-003, TC-005, TC-006 pasan (para estas dos pantallas).
- [ ] `Tarjetas.test.tsx` y `Suscripciones.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí.
