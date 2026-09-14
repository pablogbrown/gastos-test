# Progress — Autenticación Frontend

## Checklist

### Tasks
- [x] T1 — Pantallas Login y Registro
- [x] T2 — Sesión JWT: guardar, enviar, logout automático en 401
- [x] T3 — Selector de casas y gate del shell existente
- [x] T4 — Adaptar tests existentes y documentación

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Sin JWT guardado se muestra Login
- [x] `[TC-002]` *[UNIT]* — Registro válido llama a la API y termina en Login
- [x] `[TC-003]` *[UNIT]* — Requests posteriores al login incluyen Authorization Bearer
- [x] `[TC-004]` *[UNIT]* — Un 401 dispara logout automático
- [x] `[TC-005]` *[UNIT]* — Usuario con 2 casas ve el selector
- [x] `[TC-006]` *[UNIT]* — Cerrar sesión borra el JWT y vuelve a Login
- [x] `[TC-007]` *[E2E]* — Flujo completo registro→login→crear casa→navegar shell — verificado por la sesión coordinadora con Chrome real (ver nota)

#### Outcome Smoke Test
Verificado en vivo por la sesión coordinadora (el builder no tenía
navegador ni backend+frontend corriendo juntos disponibles): backend
real (`uvicorn`) + frontend real (`vite`, proxy a `/auth` y `/casas`) +
Chrome real. Flujo completo: `POST /auth/registro` (vía curl) → Login
en la UI → sesión establecida → "Tus casas" vacío → Crear casa → shell
existente con navegación superior (viewport ancho) poblado
correctamente (Miembros/Gastos/Balance/Tareas/Ranking) → "Cerrar
sesión" vuelve a Login → re-login → "Casa E2E" sigue en el selector →
entrar de nuevo muestra el mismo estado. Sin errores de consola.

## Completion Summary
Las 4 tasks implementadas end-to-end con TDD: pantallas Login/Registro
(MUI, mismo tema de `ui-modernization`), sesión JWT centralizada en
`authClient.ts` (guardar/leer/borrar + `fetchAutenticado` con logout
automático en 401), selector de casas + gate de 3 estados en `App.tsx`
(Login/Registro → SelectorCasas → shell existente), y los 4 clientes de
API existentes migrados de `X-Usuario-Id` a `Authorization: Bearer <jwt>`
sin cambiar su lógica de negocio. TC-001 a TC-006 en verde en el build;
TC-007 (navegador real) fue verificado posteriormente por la sesión
coordinadora — ver Outcome Smoke Test arriba y
`evidence/1/build-results.md` para el detalle del build. Suite completa:
`npm run build`/`npm run lint`/`npm run test` limpios (55/55 tests).

**Hallazgo durante esa verificación, ya corregido**: al integrar
`auth-backend` con `dockerize-local-env` por primera vez (mergeando
`main` dentro de `feat/usuarios-auth`), la migración `0001` fallaba
contra un PostgreSQL real recién creado (creaba `miembros` con una FK a
`usuarios` antes de que esa tabla existiera — SQLite no valida esto,
Postgres sí). Corregido directamente en `feat/usuarios-auth` (no en
esta branch), verificado con `docker compose up` desde cero + flujo
JWT completo contra Postgres real.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 7 test cases. |
| 2 | 2026-09-14 | execute | T1 | TC-001, TC-002 | `Login.tsx`/`Registro.tsx` (MUI) + `authClient.ts` (login/registrar contra `auth-backend`). |
| 3 | 2026-09-14 | execute | T2 | TC-003, TC-004 | Sesión JWT en `authClient.ts` (guardarSesion/obtenerToken/cerrarSesion/fetchAutenticado); `httpError.ts` extraído para evitar import circular; los 4 clientes existentes migrados a `Authorization: Bearer`. |
| 4 | 2026-09-14 | execute | T3 | TC-005, TC-006 | `SelectorCasas.tsx` (`GET /casas/mias`); `App.tsx` reestructurado como gate de 3 estados; botón "Cerrar sesión" en `AppNav.tsx`. |
| 5 | 2026-09-14 | execute | T4 | — | Tests existentes adaptados al flujo de sesión (7 pantallas pierden `usuarioId`, `Tareas.tsx` lo conserva); README actualizado. |
| 6 | 2026-09-14 | verify | — | 55/55 (unit) | `npm run build`/`npm run lint`/`npm run test` limpios. Fix de entorno: Node ≥ 22 sombrea `localStorage` de jsdom bajo Vitest — `--no-experimental-webstorage` agregado a `vite.config.ts`. TC-007 (E2E navegador real) no verificable en este sandbox. |
