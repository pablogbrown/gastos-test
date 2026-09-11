# Task 3 — Selector de casas y gate del shell existente

## Scope
- `src/frontend/pages/SelectorCasas.tsx` (nuevo).
- `src/frontend/App.tsx` — reestructurar como gate: Login / Selector / Shell.

## Changes
### Frontend — Shell Gate
- `SelectorCasas.tsx`: lista (`List`/`Card` de MUI) de las casas del usuario (`GET /casas/mias`, de `auth-backend`), cada una navega al shell existente para esa casa; botón "Crear nueva casa" reutiliza `CrearCasa.tsx` ya existente.
- `App.tsx`: sin JWT → `Login`/`Registro`; con JWT y sin casa elegida → `SelectorCasas`; con JWT y casa elegida → el shell existente (`ui-modernization`), pasándole la casa elegida — la navegación INTERNA del shell (bottom nav / top bar) no cambia, solo qué lo precede.
- Botón "Cerrar sesión" visible desde el shell (llama a `cerrarSesion()` de T2 y vuelve a `Login`) — TC-006.

## Design Rationale
Modelar el flujo como un gate de 3 estados (Login → Selector → Shell) en vez de meter condicionales dispersos por todo `App.tsx` mantiene la lógica de "qué se muestra cuándo" en un solo lugar legible.

## Dependencies
T2 (sesión JWT y clientes ya migrados).

## Done When
- [ ] TC-005, TC-006 pasan.
- [ ] Un usuario con 2 casas ve el selector; uno con 1 sola casa puede seguir entrando directo o vía el selector (decisión de implementación, ambas válidas mientras el flujo con 2+ casas funcione).
- [ ] Build succeeds.

## Interfaces Produced
Ninguno nuevo (compone lo producido por T1/T2).

## Standalone Verifiable
Sí, una vez T2 existe.
