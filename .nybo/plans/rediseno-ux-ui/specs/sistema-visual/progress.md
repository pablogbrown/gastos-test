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
- [x] Verificación (spec-level, una sola pasada tras completar T1–T4)

### Curate
- [x] Curación de hallazgos post-verify

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
| 1 | 2026-09-23 | Build/lint/tests verdes (163/163, 25 archivos, 0 regresión). | resolved |
| 2 | 2026-09-23 | Coverage no disponible (sin proveedor instalado) — decision class `new-dependency`, diferida a un humano. Ver `decisions.yaml` D001. | open |
| 3 | 2026-09-23 | Live evidence capturada vía Playwright (Chrome del sistema) contra un dev server aislado de este worktree: tema nuevo, PageHeader, EmptyState y nav restyled confirmados en desktop y mobile. Ver `evidence/1/screenshots/`. | resolved |
| 4 | 2026-09-23 | Caso `[HUMAN]` de T4 (smoke visual en emulador Android) no ejecutado por BUILD — queda diferido al checkpoint humano. | open |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 4 tasks, 9 test cases. |
| 2 | 2026-09-23 | build | ready | live (Playwright, desktop+mobile) | T1–T4 implementados, 163/163 tests verdes, 0 regresión. Coverage diferido (new-dependency, D001). Android `[HUMAN]` smoke diferido al checkpoint. |
