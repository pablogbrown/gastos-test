# Task 1 — Design system, tema, shell responsivo y CrearCasa

## Scope
- `package.json` — nuevas dependencias: `@mui/material`, `@mui/icons-material`, `@emotion/react`, `@emotion/styled`.
- `src/frontend/theme.ts` — tema MUI (paleta, tipografía, overrides de `BottomNavigationAction`).
- `src/frontend/App.tsx` — `ThemeProvider` + shell responsivo (bottom nav / top bar).
- `src/frontend/pages/CrearCasa.tsx` — restyle con componentes MUI.
- `src/frontend/main.tsx` — envolver con `ThemeProvider`/`CssBaseline` si no está ya en `App.tsx`.

## Changes
### Frontend — Design System
- Instalar MUI y sus peer dependencies; confirmar que la versión es compatible con React 18 (ya en `package.json`).
- `theme.ts`: exporta un tema `createTheme(...)` con paleta y tipografía; los `BottomNavigationAction` reciben `sx={{ minHeight: 44 }}` (o equivalente) para cumplir REQ-004.
- `App.tsx`: envuelve la app en `ThemeProvider theme={theme}` + `CssBaseline`; usa `useMediaQuery(theme.breakpoints.up('sm'))` para decidir entre `BottomNavigation` (mobile) y `AppBar` con `Tabs` (desktop), manteniendo el mismo estado `pantalla`/`setPantalla` ya existente — solo cambia el markup de navegación, no la lógica de qué pantalla se muestra.
- `CrearCasa.tsx`: formulario reconstruido con `TextField` + `Button` de MUI, mismo comportamiento (llama a `crearCasa` del cliente existente sin cambios).

## Design Rationale
Concentrar el tema y el shell en una sola task establece la base (paleta, breakpoints, patrón de navegación) que las demás pantallas (T2, T3) consumen — evita que cada pantalla defina su propio estilo ad-hoc.

## Dependencies
Ninguna — primer task de la spec.

## Done When
- [ ] TC-001, TC-002, TC-004 pasan.
- [ ] `npm run build` y `npm run lint` limpios con las nuevas dependencias.
- [ ] `CrearCasa` sigue funcionando end-to-end contra la API real (mismo flujo ya verificado manualmente).

## Interfaces Produced
- `{name: "theme", signature: "Theme (MUI createTheme)", kind: "export"}`

## Standalone Verifiable
Sí — el shell y `CrearCasa` se pueden verificar de punta a punta sin que existan T2/T3 (las demás pantallas siguen sin estilo hasta que corran).
