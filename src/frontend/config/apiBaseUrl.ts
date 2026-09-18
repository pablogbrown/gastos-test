/**
 * Base URL de la API para builds donde no existe el proxy server-side de
 * Vite (`/casas`, `/auth`, ... resueltos hoy por `vite.config.ts` +
 * `apiProxyTarget.ts`) — el caso del WebView de Capacitor, que carga
 * `dist/` como un bundle estático servido desde `capacitor://localhost`
 * y necesita una URL absoluta para llegar al backend (T1,
 * android-capacitor-app).
 *
 * Mismo patrón testeable que `apiProxyTarget.ts` (parámetro `env`
 * inyectable) pero leyendo `import.meta.env` en vez de `process.env`:
 * `apiProxyTarget.ts` resuelve el proxy target en tiempo de build/Node
 * (`vite.config.ts`), este módulo resuelve la base URL en tiempo de
 * ejecución del bundle ya compilado, dentro del navegador/WebView.
 *
 * Sin `VITE_API_BASE_URL`, devuelve "" — el comportamiento actual (rutas
 * relativas, sin cambio para el despliegue web) queda exactamente igual.
 */
export function getApiBaseUrl(
  env: Record<string, string | undefined> = import.meta.env
): string {
  return env.VITE_API_BASE_URL || "";
}
