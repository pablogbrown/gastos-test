# Task 4 — UI: Creación de Casa y Gestión de Miembros

## Scope
- `src/frontend/pages/CrearCasa.tsx`
- `src/frontend/pages/Miembros.tsx`
- `src/frontend/api/casasClient.ts`

## Changes
### UI
- Formulario "Crear casa" (nombre) que llama a `POST /casas` y redirige a la pantalla de la casa creada.
- Pantalla "Miembros": tabla de miembros con estado (activo/inactivo), formulario de alta (nombre + identificación), acción "Desactivar" visible solo para Administrador (oculta según rol vía `permisos` de T2).
- Mensajes de error visibles para nombre vacío, identificación duplicada y falta de permisos (TC-002, TC-004, TC-006).

## Design Rationale
La UI consulta el rol del usuario actual para ocultar acciones no permitidas, pero la autorización real ya está garantizada en la API (T3) — defensa en profundidad, no doble fuente de verdad.

## Dependencies
T3 (API routes).

## Done When
- [ ] Crear casa y agregar miembro funcionan end-to-end contra la API real.
- [ ] Acción "Desactivar" oculta para rol Miembro.
- [ ] Build succeeds, no errores de tipos.

## Interfaces Produced
Ninguno consumido por otras tasks (task final de la spec).

## Standalone Verifiable
Sí, una vez T3 desplegado.
