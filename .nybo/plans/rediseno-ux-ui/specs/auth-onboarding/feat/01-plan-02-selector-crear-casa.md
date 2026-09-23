# T2 — Selector de casas + Crear casa

## Scope
- `src/frontend/pages/SelectorCasas.tsx`
- `src/frontend/pages/CrearCasa.tsx`

## Changes
- Mismo layout centrado que T1 (Login/Registro) — consistencia visual en todo el flujo previo al shell principal de la app.
- Selector de casas: cada casa como tarjeta seleccionable (no una lista de opciones de texto).
- Crear casa: formulario dentro de la misma tarjeta centrada.

## Implementation Steps
1. Baseline: confirmar `SelectorCasas.test.tsx` en verde.
2. Aplicar el mismo layout centrado que T1.
3. Reconstruir la lista de casas como tarjetas seleccionables.
4. Re-correr el suite sin modificar queries.

## Design Rationale
Mantener el mismo lenguaje visual desde Login hasta el Selector de casas evita que el usuario perciba un salto de calidad/estilo entre pantallas consecutivas del mismo flujo.

## Dependencies
Ninguna formal dentro de esta spec (T1 y T2 son independientes entre sí), pero reutiliza el mismo patrón de tarjeta centrada establecido en T1 por consistencia.

## Done When
- [ ] TC-003, TC-004 pasan.
- [ ] `SelectorCasas.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí.
