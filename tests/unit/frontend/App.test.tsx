import { ThemeProvider } from "@mui/material/styles";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { TOKEN_STORAGE_KEY } from "../../../src/frontend/api/authClient";
import { App } from "../../../src/frontend/App";
import { theme } from "../../../src/frontend/theme";

const CASA = {
  id: "11111111-1111-1111-1111-111111111111",
  nombre: "Casa del centro",
  creado_en: "2026-01-01T00:00:00",
  miembros: [],
};

/** Un JWT sintético válido para las pruebas de `App` — no necesita firma
 * real: `obtenerUsuarioIdActual()` solo decodifica el payload, y el
 * backend (mockeado acá) nunca lo verifica en estos tests. */
function jwtFalso(sub = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"): string {
  const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const payload = btoa(JSON.stringify({ sub, exp: 9999999999 }));
  return `${header}.${payload}.firma-invalida`;
}

function mockMatchMedia(matches: boolean) {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

function renderApp() {
  return render(
    <ThemeProvider theme={theme}>
      <App />
    </ThemeProvider>
  );
}

describe("App — gate de sesión", () => {
  afterEach(() => {
    localStorage.clear();
    vi.unstubAllGlobals();
  });

  it("TC-001: sin JWT guardado se muestra Login, no el shell existente", () => {
    mockMatchMedia(true);

    renderApp();

    expect(screen.getByLabelText("Iniciar sesión")).toBeInTheDocument();
    expect(screen.queryByRole("tablist", { name: "Navegación" })).not.toBeInTheDocument();
    expect(screen.queryByRole("navigation", { name: "Navegación" })).not.toBeInTheDocument();
  });

  it("TC-006: con sesión y una casa elegida, 'Cerrar sesión' borra el JWT y vuelve a Login", async () => {
    mockMatchMedia(true);
    localStorage.setItem(TOKEN_STORAGE_KEY, jwtFalso());
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/casas/mias")) {
          return { ok: true, status: 200, json: async () => [CASA] };
        }
        if (url.endsWith("/miembros")) {
          return { ok: true, status: 200, json: async () => [] };
        }
        if (url.endsWith("/inicio")) {
          return {
            ok: true,
            status: 200,
            json: async () => ({
              miembros: [],
              gastosRecientes: [],
              balance: [],
              tareasPendientes: [],
              tareasCompletadasRecientes: [],
              ranking: [],
            }),
          };
        }
        return { ok: true, status: 200, json: async () => ({}) };
      })
    );

    renderApp();

    // Selector de casas -> elegir la única casa disponible.
    const user = userEvent.setup();
    await user.click(await screen.findByText("Casa del centro"));

    // Ya en el shell: se ve la navegación existente.
    expect(await screen.findByRole("tablist", { name: "Navegación" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Cerrar sesión" }));

    expect(await screen.findByLabelText("Iniciar sesión")).toBeInTheDocument();
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull();
  });
});
