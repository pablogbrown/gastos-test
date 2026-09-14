/// <reference types="vitest" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

import { getApiProxyTarget } from "./src/frontend/config/apiProxyTarget";

export default defineConfig({
  plugins: [react()],
  root: ".",
  build: {
    outDir: "dist",
  },
  server: {
    proxy: {
      "/casas": getApiProxyTarget(),
      // Spec `usuarios-auth`: Login/Registro llaman a `/auth/login` y
      // `/auth/registro` directamente (mismo dominio en dev, vía Vite),
      // igual que `/casas` ya lo hacía para el resto de la API.
      "/auth": getApiProxyTarget(),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/frontend/test/setup.ts"],
    include: ["tests/unit/frontend/**/*.test.tsx"],
    // Spec `usuarios-auth`: Node >= 22 expone su propio `localStorage`
    // global (detrás de `--experimental-webstorage`, activo por default
    // en algunas versiones) que tapa el `window.localStorage` de jsdom y
    // no queda inicializado sin `--localstorage-file` — sin este flag,
    // `authClient.ts` (que usa `localStorage` real, como pide la spec)
    // falla en el worker de tests con "localStorage.getItem is not a
    // function". Deshabilitarlo dentro del pool de test deja que jsdom
    // provea el `localStorage` real que se está probando.
    poolOptions: {
      forks: { execArgv: ["--no-experimental-webstorage"] },
      threads: { execArgv: ["--no-experimental-webstorage"] },
    },
  },
});
