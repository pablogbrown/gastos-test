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
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/frontend/test/setup.ts"],
    include: ["tests/unit/frontend/**/*.test.tsx"],
  },
});
