# T3 — Préstamos

## Scope
- `src/frontend/pages/Prestamos.tsx`

## Changes
- Encabezado vía `PageHeader` (acción "Nuevo préstamo").
- Cada préstamo como tarjeta de línea con chip de estado — incluyendo el caso "Rechazado" (`palette.error`), "Pendiente de confirmación" (`palette.warning`), "Pendiente"/"Pagado" (warning/success), consistentes con los mismos colores usados en Gastos/Tarjetas para sus propios estados.
- Botones de Confirmar/Rechazar (solo visibles a la parte pendiente, lógica ya existente) preservados sin cambio de comportamiento.
- Sin préstamos → `EmptyState`.

## Implementation Steps
1. Baseline: confirmar `Prestamos.test.tsx` en verde.
2. Reemplazar encabezado por `PageHeader`.
3. Reconstruir la lista como tarjetas de línea con chip semántico por cada uno de los 4 estados posibles.
4. Agregar `EmptyState`.
5. Re-correr el suite sin modificar queries.

## Design Rationale
Préstamos tiene 4 estados posibles distintos (más que cualquier otra pantalla financiera) — separarlo en su propio task evita que su complejidad de estado se mezcle con el resto y facilita verificar TC-002 de forma aislada.

## Dependencies
Ninguna dentro de esta spec.

## Done When
- [ ] TC-002, TC-006 pasan (para esta pantalla).
- [ ] `Prestamos.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí.
