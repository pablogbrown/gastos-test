# Sistema visual - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [x] T1 — Theme tokens (`theme.ts`)
- [x] T2 — Componentes compartidos (`PageHeader`, `StatCard`, `EmptyState`)
- [x] T3 — Restyle del shell de navegación (`AppNav.tsx`)
- [x] T4 — `InicioCasa.tsx` como pantalla bandera

### Verify
- [ ] Verificación (spec-level, una sola pasada tras completar T1–T4)

### Curate
- [ ] Curación de hallazgos post-verify

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — el tema exportado no usa los valores por defecto de MUI ni de ui-modernization.
- [x] `[TC-002]` *[UNIT]* — un `Card` tiene borde redondeado ≥12px y sombra de elevación.
- [x] `[TC-003]` *[UNIT]* — `PageHeader` renderiza título y dispara la acción primaria.
- [x] `[TC-004]` *[UNIT]* — `EmptyState` sin acción muestra ícono + mensaje, sin botón.
- [x] `[TC-005]` *[UNIT]* — `StatCard` muestra etiqueta y valor con jerarquía tipográfica distinta.
- [x] `[TC-006]` *[UNIT]* — el ítem activo de `BottomNavigation` queda marcado como seleccionado.
- [x] `[TC-007]` *[INTEGRATION]* — la agrupación desktop (`GRUPOS_DESKTOP`) sigue funcionando sin regresión.
- [x] `[TC-008]` *[INTEGRATION]* — `InicioCasa` preserva toda su información existente tras el restyle.
- [x] `[TC-009]` *[UNIT]* — sin gastos recientes, Inicio muestra `EmptyState`.

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| — | — | Not yet started. | not started |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 4 tasks, 9 test cases. |
