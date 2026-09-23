# T1 — Gastos + Balance

## Scope
- `src/frontend/pages/Gastos.tsx`
- `src/frontend/pages/Balance.tsx`

## Changes
- Encabezado de ambas pantallas vía `PageHeader` (Gastos: acción "Nuevo gasto"; Balance: sin acción, es de solo lectura).
- Lista de gastos reconstruida como tarjetas de línea con chip de estado (pagado/a_pagar) usando los colores semánticos del tema.
- Selector de mes (ya existente en ambas) preservado tal cual, solo restyled.
- Balance: las secciones "Pesos"/"Dólares" y el desglose de aporte por miembro usan `StatCard` para los totales destacados.
- Mes sin gastos → `EmptyState`.

## Implementation Steps
1. Baseline: confirmar `Gastos.test.tsx`/`Balance.test.tsx` en verde antes del cambio.
2. Reemplazar encabezados por `PageHeader`.
3. Reconstruir la lista de gastos como tarjetas de línea con chip semántico.
4. Reconstruir los totales de Balance con `StatCard`.
5. Agregar `EmptyState` para mes sin gastos.
6. Re-correr ambos suites sin modificar queries.

## Design Rationale
Gastos y Balance comparten el mismo dato base (gastos del mes) y se editan en la misma sesión de trabajo — agruparlos evita reconstruir el mismo patrón de chip/monto dos veces por separado.

## Dependencies
Ninguna dentro de esta spec — consume `PageHeader`/`EmptyState`/`StatCard`/tema de `sistema-visual`.

## Done When
- [ ] TC-001, TC-004, TC-006 pasan (para estas dos pantallas).
- [ ] `Gastos.test.tsx` y `Balance.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí — ambas pantallas tienen su propio test suite ya existente que cubre su comportamiento de forma aislada.
