# T4 — Inicio como pantalla bandera

## Scope
- `src/frontend/pages/InicioCasa.tsx` — reconstrucción visual, cero cambio de lógica/datos.
- `tests/unit/frontend/InicioCasa.test.tsx` — no se modifican las queries existentes.

## Changes
- Encabezado de la pantalla vía `PageHeader` (título "Inicio", sin acción primaria — o con una si ya existe un CTA equivalente hoy).
- Balance/resumen y métricas puntuales (aporte, meta de la casa) vía `StatCard`.
- Banners de alerta (tarjetas próximas a vencer, mantenimiento próximo) preservados tal cual — solo restyled bajo el nuevo tema, sin cambiar su lógica de cálculo (`dashboard_service.py` no se toca).
- Lista de "gastos recientes" y mini-ranking preservados; cuando la lista de gastos recientes está vacía, usar `EmptyState` en vez de una lista vacía sin mensaje (comportamiento nuevo, TC-009).

## Implementation Steps
1. Confirmar `InicioCasa.test.tsx` en verde ANTES del cambio (baseline).
2. Reemplazar el encabezado por `PageHeader`.
3. Reemplazar las tarjetas de resumen/balance por `StatCard`.
4. Restyle de los banners de alerta bajo el nuevo tema (sin tocar su condición de aparición).
5. Agregar `EmptyState` para la lista de gastos recientes vacía.
6. Re-correr `InicioCasa.test.tsx` sin modificar sus queries — confirmar cero regresión.
7. Smoke visual manual en el emulador Android (TC-008's gate `[HUMAN]`).

## Design Rationale
Inicio es la pantalla más visitada y la que mejor demuestra el sistema de diseño completo (encabezado + estadísticas + estado vacío + navegación) — sirve de referencia concreta para las 3 specs de aplicación siguientes en vez de una descripción abstracta.

## Dependencies
T1 (tema), T2 (componentes compartidos).

## Done When
- [ ] TC-008, TC-009 pasan.
- [ ] `InicioCasa.test.tsx` completo en verde, queries sin modificar.
- [ ] Smoke visual confirmado en Android/emulador.

## Interfaces Produced
Ninguna (pantalla, no componente reutilizable).

## Standalone Verifiable
No completamente — el smoke visual `[HUMAN]` requiere ver la pantalla renderizada en el emulador/navegador, no solo el test suite automatizado.
