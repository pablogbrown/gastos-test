# Task 4 — Pulido responsivo, adaptación de tests y docs

## Scope
- Las 8 pantallas de T1/T2/T3 (pases de ajuste, no reescritura).
- `tests/unit/frontend/*.test.tsx` — adaptar a la nueva estructura MUI donde el DOM cambió.
- `README.md` — mención de la dependencia MUI.

## Changes
### Frontend — Polish + Tests
- Revisar las 8 pantallas contra un viewport de 360×800 (Chrome DevTools o Playwright): sin scroll horizontal, sin texto cortado, sin controles superpuestos (TC-006).
- Confirmar que los estilos de `BottomNavigationAction` cumplen el mínimo de 44px en la práctica, no solo en el tema (TC-004, verificación final).
- Adaptar los tests de frontend existentes (`Miembros.test.tsx`, `Gastos.test.tsx`, `Tareas.test.tsx`, `InicioCasa.test.tsx`, `HistorialActividad.test.tsx`, y cualquier otro afectado) a los nuevos selectores/roles de MUI, sin cambiar qué comportamiento verifican (TC-005) — usar `getByRole` sobre las semánticas de MUI en vez de selectores frágiles por clase.
- Actualizar el `README.md` para mencionar la dependencia de Material UI.

## Design Rationale
Separar el pulido/verificación final y la adaptación de tests en su propia task evita mezclar "construir la pantalla" con "confirmar que no rompió nada" — dos responsabilidades distintas (SRP a nivel de task).

## Dependencies
T2 y T3 (todas las pantallas deben estar restyled antes de esta pasada final).

## Done When
- [ ] TC-005, TC-006 pasan.
- [ ] La suite completa de tests de frontend pasa (`npm run test`).
- [ ] `npm run build` y `npm run lint` limpios.

## Interfaces Produced
Ninguno (task final de la spec).

## Standalone Verifiable
No en aislamiento — depende de que T1, T2 y T3 estén completas.
