# Task 2 — Sesión JWT: guardar, enviar, logout automático en 401

## Scope
- `src/frontend/api/authClient.ts` — agrega manejo de sesión (guardar/leer/borrar JWT).
- `src/frontend/api/casasClient.ts`, `gastosClient.ts`, `tareasClient.ts`, `dashboardClient.ts` — reemplazar el envío de `X-Usuario-Id` por `Authorization: Bearer <jwt>`.
- `src/frontend/App.tsx` — lógica de logout automático en 401.

## Changes
### Frontend — Session
- `authClient.ts`: `guardarSesion(token)` (localStorage), `obtenerToken()`, `cerrarSesion()` (borra el token).
- Los 4 clientes existentes dejan de recibir `usuarioId` como parámetro y en cambio agregan el header `Authorization: Bearer ${obtenerToken()}` a cada `fetch` — mismo shape de respuesta, mismo comportamiento funcional, solo cambia cómo se identifica al actor (TC-003).
- Cualquier respuesta 401 de cualquier cliente dispara `cerrarSesion()` y notifica a `App.tsx` para volver a mostrar `Login` (TC-004).

## Design Rationale
Centralizar el manejo de sesión en `authClient.ts` (en vez de que cada cliente lea `localStorage` por su cuenta) evita duplicar la misma lógica 4 veces y es el único lugar que cambia si mañana se reemplaza `localStorage` por otro mecanismo.

## Dependencies
T1 (pantallas de Login/Registro y `authClient.ts` base).

## Done When
- [ ] TC-003, TC-004 pasan.
- [ ] Ningún cliente existente envía ya `X-Usuario-Id`.
- [ ] Build succeeds.

## Interfaces Produced
- `{name: "guardarSesion", signature: "(token: string) => void", kind: "function"}`
- `{name: "obtenerToken", signature: "() => string | null", kind: "function"}`
- `{name: "cerrarSesion", signature: "() => void", kind: "function"}`

## Standalone Verifiable
Sí, una vez T1 existe.
