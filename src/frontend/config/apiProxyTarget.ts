/**
 * Target del proxy /casas usado por vite.config.ts. Extraído a su propio
 * módulo (T2, dockerize-local-env) para que sea testeable sin importar
 * vite.config.ts en sí — importarlo desde un test arrastra 'vite' y
 * '@vitejs/plugin-react', lo que rompe esbuild bajo vitest en algunos
 * entornos (ver tests/unit/frontend/vite-proxy-config.test.tsx).
 *
 * Sin VITE_API_PROXY_TARGET, apunta a 127.0.0.1:8000 — igual que antes de
 * esta spec. docker-compose la setea a `http://backend:8000`.
 */
// Declaración ambiente mínima: el proyecto no tiene @types/node (no se
// agrega una dependencia nueva solo para tipar `process`, que ya existe
// en runtime tanto bajo Node (vite.config.ts, vitest) como en el proceso
// de docker-compose).
declare const process: { env: Record<string, string | undefined> };

export function getApiProxyTarget(
  env: Record<string, string | undefined> = process.env
): string {
  return env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";
}
