# T1 — Theme tokens

## Scope
- `src/frontend/theme.ts` — reemplazar la paleta/tipografía/forma actuales.
- `tests/unit/frontend/MuiRestyle.test.tsx` — nuevo test de los tokens del tema.

## Changes

**Tema ("Cálido minimal", ver spec.md D-01):**
- `palette.primary.main`: verde/teal profundo (p.ej. `#1b6b5c` o similar, a definir por contraste AA sobre blanco).
- `palette.secondary.main`: un acento cálido complementario (p.ej. ámbar/terracota) para CTAs secundarios.
- Colores semánticos de estado (`pagado`/`a_pagar`/`pendiente`/`rechazado`) definidos como `palette.success`/`palette.warning`/`palette.error` reutilizando los slots estándar de MUI en vez de colores ad-hoc por pantalla.
- `palette.background.default`: off-white cálido (no gris frío `#f5f5f7` actual).
- `typography`: define escala completa (`h1`-`h6`, `body1`, `body2`, `caption`) con pesos explícitos; mantiene el `fontFamily` de sistema ya usado (sin agregar web fonts externas — evita costo de carga).
- `shape.borderRadius`: 16 (desde el 4 por defecto).
- `components.MuiCard.styleOverrides.root`: sombra suave (`boxShadow` definido, no `none` ni el `elevation` duro por defecto).
- Preservar los `MuiBottomNavigationAction`/`MuiBottomNavigation` `styleOverrides` de accesibilidad (44px/56px) ya existentes — no tocar esa parte.

## Implementation Steps
1. Definir la nueva paleta y confirmar contraste AA (texto sobre fondo) con una herramienta de contraste antes de fijar los valores hex.
2. Reescribir `typography` con la escala completa.
3. Agregar `shape: { borderRadius: 16 }`.
4. Agregar `components.MuiCard.styleOverrides.root` con sombra suave.
5. Escribir `MuiRestyle.test.tsx`: importar `theme`, aserciones sobre `palette`/`shape`, y un render mínimo de `<Card>` bajo `ThemeProvider` verificando el estilo computado.
6. Correr `npm run build` para confirmar que ningún tipo se rompe.

## Design Rationale
Chose A (Cálido minimal): un solo archivo (`theme.ts`) sigue siendo la única fuente de verdad de estilo (principio de Clarity/Consistency del proyecto) — cero cambio estructural, solo valores. Menor superficie de riesgo que migrar a tokens tonales (Opción C).

## Dependencies
Ninguna — es la base de la que dependen T2, T3 y T4.

## Done When
- [ ] `theme.ts` exporta la nueva paleta/tipografía/forma/elevación.
- [ ] `MuiRestyle.test.tsx` (TC-001, TC-002) pasa.
- [ ] `npm run build` compila sin error de tipos.

## Interfaces Produced
- `theme` (export existente, valores cambiados) — `Theme`.

## Standalone Verifiable
Sí — el cambio de tema es completamente verificable de forma aislada (tests sobre el objeto `theme` y un render mínimo de `Card`), sin depender de ninguna pantalla real.
