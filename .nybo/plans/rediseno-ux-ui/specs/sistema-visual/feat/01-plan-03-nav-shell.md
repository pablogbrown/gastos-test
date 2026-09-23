# T3 — Shell de navegación restyled

## Scope
- `src/frontend/AppNav.tsx` — restyle únicamente, sin tocar `SECCIONES`/`GRUPOS_DESKTOP` ni el breakpoint `sm`.
- `tests/unit/frontend/AppShell.test.tsx` — no se modifican las queries existentes; se agregan las nuevas si hace falta cubrir el estado activo.

## Changes
- Mobile (`BottomNavigation`): el ítem activo se destaca con el nuevo `palette.primary` (relleno o indicador, no solo el color de ícono por defecto de MUI).
- Desktop (`AppBar`/`GRUPOS_DESKTOP`): el botón/grupo activo se destaca de forma consistente con mobile (mismo tratamiento de color primario).
- Ningún cambio a la lógica de agrupación (`GRUPOS_DESKTOP`), al breakpoint (`useMediaQuery` sobre `sm`), ni a las 16 rutas ya cableadas.

## Implementation Steps
1. Confirmar que `AppShell.test.tsx` pasa en verde ANTES del cambio (baseline).
2. Aplicar el restyle del ítem activo en mobile.
3. Aplicar el restyle del botón/grupo activo en desktop.
4. Re-correr `AppShell.test.tsx` sin modificar sus queries — confirmar cero regresión.

## Design Rationale
El shell de navegación ya vive en su propio componente testeable (`FRONTEND-002`, convención establecida) — este task solo cambia estilo, preservando esa separación y sin tocar el árbol de decisión de agrupación desktop.

## Dependencies
T1 (nuevo tema).

## Done When
- [ ] TC-006, TC-007 pasan.
- [ ] `AppShell.test.tsx` completo en verde, queries sin modificar.

## Interfaces Produced
Ninguna (componente de presentación, sin exports nuevos).

## Standalone Verifiable
Sí — el suite de `AppShell.test.tsx` ya cubre el componente de forma aislada del resto de la app.
