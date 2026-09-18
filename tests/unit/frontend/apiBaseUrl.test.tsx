/**
 * T1 (android-capacitor-app) — TC-001/TC-002 a nivel de módulo:
 * `getApiBaseUrl` devuelve "" por default (comportamiento web actual,
 * rutas relativas sin cambio) y respeta `VITE_API_BASE_URL` cuando está
 * seteada (necesaria porque el APK de Capacitor no tiene el proxy de
 * Vite que hoy resuelve rutas relativas contra el backend).
 *
 * Mismo patrón testeable que `apiProxyTarget.ts`/
 * `vite-proxy-config.test.tsx`: parámetro `env` inyectable en vez de
 * depender de `import.meta.env` real.
 */
import { describe, expect, it } from "vitest";

import { getApiBaseUrl } from "../../../src/frontend/config/apiBaseUrl";

describe("getApiBaseUrl", () => {
  it("TC-001: devuelve '' por default — rutas relativas, igual que hoy", () => {
    expect(getApiBaseUrl({})).toBe("");
  });

  it("TC-002: respeta VITE_API_BASE_URL cuando está seteada", () => {
    expect(getApiBaseUrl({ VITE_API_BASE_URL: "http://192.168.1.5:8000" })).toBe(
      "http://192.168.1.5:8000"
    );
  });
});
