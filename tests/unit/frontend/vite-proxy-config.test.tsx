/**
 * T2 (dockerize-local-env) — regresión: el proxy de /casas debe seguir
 * apuntando a 127.0.0.1:8000 por default (sin Docker), y respetar
 * VITE_API_PROXY_TARGET cuando docker-compose la setea al servicio
 * `backend`. Extensión .tsx (no .ts) porque el include de vitest en
 * vite.config.ts solo matchea tests/unit/frontend/**\/*.test.tsx.
 *
 * Importa desde src/frontend/config/apiProxyTarget.ts, no desde
 * vite.config.ts directamente — importar vite.config.ts arrastra 'vite' y
 * '@vitejs/plugin-react', lo que rompe esbuild bajo vitest en algunos
 * entornos.
 */
import { describe, expect, it } from "vitest";

import { getApiProxyTarget } from "../../../src/frontend/config/apiProxyTarget";

describe("getApiProxyTarget", () => {
  it("usa 127.0.0.1:8000 por default, igual que antes de esta spec", () => {
    expect(getApiProxyTarget({})).toBe("http://127.0.0.1:8000");
  });

  it("respeta VITE_API_PROXY_TARGET cuando está seteada (caso Docker)", () => {
    expect(
      getApiProxyTarget({ VITE_API_PROXY_TARGET: "http://backend:8000" })
    ).toBe("http://backend:8000");
  });
});
