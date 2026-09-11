# Task 4 — UI: Registro de Gasto, Balance e Historial

## Scope
- `src/frontend/pages/Gastos.tsx`
- `src/frontend/pages/Balance.tsx`
- `src/frontend/api/gastosClient.ts`

## Changes
### UI
- Formulario "Nuevo gasto" con selección de categoría y participantes (checkbox "todos los miembros" preseleccionado).
- Pantalla "Balance": tabla miembro/pagó/correspondía/balance + lista de transferencias sugeridas.
- Pantalla "Historial de gastos": tabla fecha/miembro/descripción/importe/categoría.

## Design Rationale
Mismo patrón de la UI de `casas-miembros`: componentes delgados que consumen la API real, sin lógica de negocio duplicada en el cliente.

## Dependencies
T3.

## Done When
- [ ] Flujo registrar gasto → ver balance → ver historial funciona end-to-end.
- [ ] Build succeeds.

## Interfaces Produced
Ninguno (task final).

## Standalone Verifiable
Sí, una vez T3 desplegado.
