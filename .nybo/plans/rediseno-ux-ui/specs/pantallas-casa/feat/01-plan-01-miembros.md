# T1 — Miembros como tarjetas de perfil

## Scope
- `src/frontend/pages/Miembros.tsx`

## Changes
- Encabezado vía `PageHeader` (acción "Agregar miembro", solo visible a Administrador — lógica de permisos existente preservada).
- Cada miembro como `Card` con `Avatar` (inicial del nombre), nombre, chip de rol (Administrador/Miembro) y chip de estado (activo/pendiente/desactivado) — reemplazando la fila de lista plana actual.
- Botones de "Agregar"/"Desactivar" preservados con su lógica de permisos actual (`_validar_actor_admin` en el backend no cambia).

## Implementation Steps
1. Baseline: confirmar `Miembros.test.tsx` en verde.
2. Reemplazar encabezado por `PageHeader`.
3. Reconstruir cada miembro como tarjeta con `Avatar`+chips.
4. Distinguir visualmente el chip de un miembro "Pendiente" del de uno activo (color/label distinto).
5. Re-correr el suite sin modificar queries.

## Design Rationale
Un `Avatar` con inicial es el patrón estándar de MUI para representar personas — da identidad visual inmediata sin necesitar fotos de perfil (fuera de scope).

## Dependencies
Ninguna dentro de esta spec — consume `PageHeader`/tema de `sistema-visual`.

## Done When
- [ ] TC-001, TC-002, TC-007 pasan (para esta pantalla).
- [ ] `Miembros.test.tsx` en verde, queries sin modificar.

## Interfaces Produced
Ninguna.

## Standalone Verifiable
Sí.
