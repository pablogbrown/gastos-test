# Task 1 — Pantallas Login y Registro

## Scope
- `src/frontend/pages/Login.tsx` (nuevo).
- `src/frontend/pages/Registro.tsx` (nuevo).
- `src/frontend/api/authClient.ts` (nuevo).

## Changes
### Frontend — Screens
- `Login.tsx`: formulario `TextField` (email, contraseña) + `Button` "Ingresar", link a Registro. Llama a `authClient.login(email, password)`.
- `Registro.tsx`: formulario `TextField` (nombre, email, contraseña) + `Button` "Crear cuenta", link a Login. Llama a `authClient.registrar(...)`.
- `authClient.ts`: `login(email, password) -> {access_token}`, `registrar(nombre, email, password) -> {id, email}` — llaman a `POST /auth/login`/`POST /auth/registro` del backend de `auth-backend`.
- Ambas pantallas usan el `theme.ts` ya existente de `ui-modernization` — sin paleta/tipografía propia.

## Design Rationale
Un `authClient.ts` separado (en vez de meter las llamadas de auth en `casasClient.ts`) mantiene el mismo patrón de un cliente por dominio ya usado en el proyecto (`gastosClient.ts`, `tareasClient.ts`, `dashboardClient.ts`).

## Dependencies
Ninguna — primer task de la spec. Requiere que `auth-backend` esté mergeado (dependencia de la spec, no de esta task específicamente).

## Done When
- [ ] TC-001, TC-002 pasan.
- [ ] `npm run build`/`npm run lint` limpios.
- [ ] Registro y login funcionan contra la API real de `auth-backend`.

## Interfaces Produced
- `{name: "login", signature: "(email: string, password: string) => Promise<{access_token: string}>", kind: "function"}`
- `{name: "registrar", signature: "(nombre: string, email: string, password: string) => Promise<{id: string, email: string}>", kind: "function"}`

## Standalone Verifiable
Sí, contra la API real de `auth-backend` ya mergeada.
