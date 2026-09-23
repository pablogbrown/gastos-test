# T4 — Mantenimiento + Mantenimiento Autos

## Scope
- `src/frontend/pages/Mantenimiento.tsx`
- `src/frontend/pages/MantenimientoAutos.tsx`

## Changes
- Encabezado de ambas vía `PageHeader` (acciones "Nuevo ítem"/agrupado por auto en Mantenimiento Autos).
- Cada ítem de mantenimiento como tarjeta de línea, con la lista de materiales (conseguido/pendiente) preservada, y la alerta de vencimiento (7 días o vencido) restyled bajo el nuevo tema sin cambiar su lógica de cálculo.
- Mantenimiento Autos: agrupación por auto preservada, solo restyled.
- Sin ítems → `EmptyState`.

## Implementation Steps
1. Baseline: confirmar ambos suites en verde.
2. Reemplazar encabezados por `PageHeader`.
3. Reconstruir ítems de mantenimiento como tarjetas de línea, preservando la lista de materiales y la alerta de vencimiento.
4. Agregar `EmptyState` donde corresponda.
5. Re-correr ambos suites sin modificar queries.

## Design Rationale
Ambas pantallas comparten literalmente la misma mecánica (ítem + materiales + alerta), difiriendo solo en si están agrupadas por auto — agruparlas en un único task evita reconstruir la misma receta dos veces por separado.

## Dependencies
Ninguna dentro de esta spec.

## Done When
- [ ] TC-006 pasa (para estas dos pantallas).
- [ ] `Mantenimiento.test.tsx` y `MantenimientoAutos.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí.
