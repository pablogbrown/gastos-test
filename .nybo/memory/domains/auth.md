# Domain: auth

auth domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- added: 2026-09-14 | feature: usuarios-auth (auth-backend) | confidence: high | verified: 2026-09-14 -->
- Backend identity resolution is centralized in `src/api/dependencies.py`:
  `get_current_usuario` (decodes the `Authorization: Bearer <jwt>` header
  via `auth_service.decodificar_token`, 401 on missing/invalid/expired)
  and `resolver_actor_en_casa` (maps the authenticated `Usuario` to their
  `Miembro` row for a given `casa_id`, 403 if not a member). Every
  protected route depends on these via FastAPI `Depends(...)` — no route
  reads `X-Usuario-Id` or any other identity header directly anymore.
  `Usuario.id` (global) and `Miembro.id` (per-casa) are deliberately
  different values since a Usuario can belong to more than one Casa; a
  new route needs the `Miembro`, not the `Usuario`, resolve it via
  `resolver_actor_en_casa`, never assume they're the same id.

## Patterns
<!-- Reusable patterns specific to this domain -->

<!-- added: 2026-09-14 | feature: resolver-rol-usuario-en-casa | confidence: high | verified: 2026-09-14 -->
- Frontend identity resolution (client-side mirror of
  `resolver_actor_en_casa`): the backend centralized global-Usuario ->
  per-casa-Miembro resolution since `usuarios-auth`, but nothing on the
  frontend mirrored it — `App.tsx` hardcoded `rolUsuarioActual="admin"`
  and passed the global `usuarioId` where a `Miembro.id` was needed,
  silently masking the exact same global-vs-per-casa conflation the
  backend already solved. Fixed by: (1) expose `usuario_id` on
  `MiembroOut` (additive; already on the ORM model, just not previously
  serialized); (2) in `App.tsx` — the same place that already loads the
  casa's full `miembros` list — resolve `miMiembro = miembros.find(m =>
  m.usuario_id === obtenerUsuarioIdActual())` once, and derive both
  `rolUsuarioActual = miMiembro?.rol ?? "member"` and the caller's own
  `Miembro.id` (`miMiembro?.id`) from it, passing both down instead of
  any hardcoded/global-id value. **Fallback is always `"member"`, never
  `"admin"`** — while `miembros` is loading or in any inconsistent state
  where the caller's own row isn't found yet, assume the
  least-privileged role; an unsafe default here is a silent
  authorization gap, not just a rendering glitch. Any prop meant to
  carry "my identity for a per-casa comparison" should be named for
  what it actually is (`miembroIdActual`, not `usuarioId`) — the prior
  generic name is what let the original bug hide in plain sight for a
  full spec cycle.

<!-- added: 2026-09-14 | feature: usuarios-auth (auth-frontend) | confidence: high | verified: 2026-09-14 -->
- Frontend session/JWT handling is centralized in one module,
  `src/frontend/api/authClient.ts` — `guardarSesion`/`obtenerToken`/
  `cerrarSesion` (localStorage), `login`/`registrar` (calls to
  `/auth/login`/`/auth/registro`), and `fetchAutenticado` (a `fetch`
  wrapper every other API client uses instead of calling `fetch`
  directly — adds `Authorization: Bearer <jwt>` and triggers
  `cerrarSesion()` on any 401). Cross-cutting "session just ended"
  notification (both an explicit logout and an automatic 401 logout) is
  a tiny pub-sub, `suscribirseACierreSesion(listener)`, so `App.tsx` can
  react without every API client needing to know about React state.
  Any new frontend API client should call `fetchAutenticado` from this
  module, never send its own `Authorization`/`X-Usuario-Id` header, and
  never read `localStorage` directly.

## Gotchas
<!-- Things that tripped us up -->

<!-- resolved: 2026-09-14 | feature: resolver-rol-usuario-en-casa | see the "Frontend identity resolution" pattern above. The 2026-09-14 (usuarios-auth) entry below about `Tareas.tsx`'s `puedeCompletar()` comparing the global Usuario.id against `tarea.responsableId` (a per-casa Miembro id) no longer applies: `App.tsx` now resolves the caller's own `Miembro.id` and passes it in (`miembroIdActual`), not the global `usuarioId`. -->
<!-- added: 2026-09-14 | feature: usuarios-auth (auth-frontend) | confidence: medium | verified: 2026-09-14 -->
- ~~`src/frontend/pages/Tareas.tsx`'s `puedeCompletar()` compares the
  authenticated Usuario's id against `tarea.responsableId`, which is
  actually a Miembro id (per-casa), not a Usuario id (global)~~ —
  **resolved by `resolver-rol-usuario-en-casa`**, see the pattern above.
