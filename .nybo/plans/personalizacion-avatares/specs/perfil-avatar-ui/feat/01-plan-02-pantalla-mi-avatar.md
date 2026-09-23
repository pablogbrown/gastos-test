# T2 — Pantalla "Mi Avatar" + navegación

## Scope
- `src/frontend/pages/MiAvatar.tsx` (nuevo)
- `src/frontend/App.tsx` (edit: registrar la pantalla)
- `src/frontend/AppNav.tsx` (edit: agregar `"miAvatar"` al grupo "Casa")

## Changes
- `MiAvatar.tsx`: usa `PageHeader` (de `sistema-visual`); `StatCard` para el saldo de créditos; sección de razas (`avatarClient.listarAvataresDisponibles` + el resto del catálogo para mostrar las bloqueadas con su nivel requerido); sección de tienda (`tiendaClient.listarCatalogoAccesorios`/`comprarAccesorio`/`equiparAccesorio`).
- `App.tsx`: agrega `"miAvatar"` a la unión de pantallas y su ruteo (mismo patrón que cualquier otra pantalla ya cableada).
- `AppNav.tsx`: agrega `{ value: "miAvatar", label: "Mi Avatar", icon: <ícono nuevo, ej. PetsIcon> }` a `SECCIONES`, y `"miAvatar"` a la lista `pantallas` del grupo `"Casa"` en `GRUPOS_DESKTOP` — NUNCA como entrada `"suelta"` nueva ni grupo nuevo (constraint de la spec).

## Implementation Steps
1. Baseline: confirmar `AppShell.test.tsx` en verde (4 ítems de primer nivel).
2. Crear `MiAvatar.tsx` con sus 3 secciones (créditos, razas, tienda).
3. Cablear en `App.tsx` y agregar a `SECCIONES`/`GRUPOS_DESKTOP.Casa` en `AppNav.tsx`.
4. RED→GREEN: `MiAvatar.test.tsx` (TC-004/005/006).
5. Actualizar `AppShell.test.tsx` con TC-007 (confirmar "Mi Avatar" dentro de "Casa", 4 ítems de primer nivel sin cambio).
6. Re-correr todo el suite de navegación — confirmar cero regresión sobre el fix `nav-mobile-agrupada` reciente.

## Design Rationale
Agregar la pantalla al grupo `"Casa"` ya existente (en vez de crear un grupo nuevo o un ítem suelto) es la única opción compatible con la restricción de navegación de esta spec — el bottom nav mobile ya está al límite recomendado de 5 ítems (`fix nav-mobile-agrupada`, guía `ui-ux-pro-max`).

## Dependencies
Ninguna dentro de esta spec — consume interfaces ya construidas de `avatares-economia` y `tienda-accesorios`, y `PageHeader`/`StatCard` de `sistema-visual`.

## Done When
- [ ] TC-004, TC-005, TC-006, TC-007 pasan.
- [ ] `AppShell.test.tsx` completo en verde — 4 ítems de primer nivel, sin regresión.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí — depende solo de interfaces ya construidas y estables de las specs anteriores.
