# T1 — Base URL de API configurable

## Scope
- Nuevo `src/frontend/config/apiBaseUrl.ts`: `getApiBaseUrl(env =
  import.meta.env): string` — devuelve `env.VITE_API_BASE_URL || ""`.
  Mismo patrón testeable que `apiProxyTarget.ts` (parámetro `env`
  inyectable para poder testear sin depender de `import.meta.env` real).
- `src/frontend/api/authClient.ts`:
  - `fetchAutenticado`: si `input` es `string` y empieza con `/`,
    anteponerle `getApiBaseUrl()` antes de pasarlo a `fetch`. `input`
    no-string (un objeto `Request`/`URL`) o que no empiece con `/`
    (ya absoluto) pasa sin modificar.
  - `registrar`/`login`: aplicar el mismo prefijo a sus dos `fetch(...)`
    directos.

## Dependencies
Ninguna (task raíz).

## Done When
- TC-001/TC-002 pasan.
- El resto de la suite frontend (129+ tests) sigue en verde sin
  modificaciones — ningún cliente de API (`gastosClient.ts`,
  `tareasClient.ts`, etc.) cambia, ya que todos pasan por
  `fetchAutenticado`.

## Verifiability
UNIT — nuevo `tests/unit/frontend/apiBaseUrl.test.tsx` para el módulo en
sí (inyectando el `env` de prueba directamente como parámetro, igual
que `vite-proxy-config.test.tsx` ya hace con `getApiProxyTarget`) +
extender `tests/unit/frontend/authClient.test.tsx` para
`fetchAutenticado`/`registrar`/`login` con y sin la env var seteada,
usando `vi.stubEnv("VITE_API_BASE_URL", "...")` de Vitest (no un
parámetro nuevo en `fetchAutenticado`, que es de uso público en todos
los clientes de API — cambiar su firma sería un blast radius
innecesario para esto).
