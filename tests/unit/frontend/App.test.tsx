import { ThemeProvider } from "@mui/material/styles";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

// Spec `perfil-avatar-ui`: Miembros ahora renderiza `AvatarConAccesorios`
// (LottieAvatar) — mismo criterio ya establecido por
// `LottieAvatar.test.tsx`/`Miembros.test.tsx`.
vi.mock("lottie-react", () => ({
  Lottie: () => <div data-testid="lottie-mock" />,
}));

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

function miembro(id: string, usuarioId: string | null, rol: "admin" | "member") {
  return {
    id,
    casa_id: CASA.id,
    usuario_id: usuarioId,
    nombre: `Miembro ${id}`,
    identificacion: id,
    rol,
    activo: true,
  };
}

function mockFetchConMiembros(miembros: unknown[]) {
  return vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/casas/mias")) {
      return { ok: true, status: 200, json: async () => [CASA] };
    }
    if (url.endsWith("/miembros")) {
      return { ok: true, status: 200, json: async () => miembros };
    }
    if (url.endsWith("/inicio")) {
      return {
        ok: true,
        status: 200,
        json: async () => ({
          miembros: [],
          gastosRecientes: [],
          balance: { totales: [], aportes: [] },
          tareasPendientes: [],
          tareasCompletadasRecientes: [],
          ranking: [],
          tarjetasConAlerta: [],
        }),
      };
    }
    return { ok: true, status: 200, json: async () => [] };
  });
}

/** Spec `nav-agrupada`: "Miembros" pasó a vivir dentro del grupo desktop
 * "Casa" del menú superior — hay que abrir ese menú antes de poder
 * elegir la pantalla, en vez de clickear un `tab` plano directo. */
async function irAPantallaMiembros() {
  const user = userEvent.setup();
  await user.click(await screen.findByText("Casa del centro"));
  await user.click(await screen.findByRole("button", { name: "Casa" }));
  await user.click(await screen.findByRole("menuitem", { name: /Miembros/ }));
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
              balance: { totales: [], aportes: [] },
              tareasPendientes: [],
              tareasCompletadasRecientes: [],
              ranking: [],
              tarjetasConAlerta: [],
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

    // Ya en el shell: se ve la navegación existente. Spec `nav-agrupada`:
    // el menú superior desktop dejó de ser un `tablist` — se verifica el
    // landmark `nav` en su lugar.
    expect(await screen.findByRole("navigation", { name: "Navegación" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Cerrar sesión" }));

    expect(await screen.findByLabelText("Iniciar sesión")).toBeInTheDocument();
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull();
  });
});

describe("App — resolución del rol real del Usuario en la casa (spec resolver-rol-usuario-en-casa)", () => {
  const SUB = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";

  afterEach(() => {
    localStorage.clear();
    vi.unstubAllGlobals();
  });

  it("TC-002: mi Miembro tiene rol member -> Miembros oculta 'Agregar miembro'", async () => {
    mockMatchMedia(true);
    localStorage.setItem(TOKEN_STORAGE_KEY, jwtFalso(SUB));
    vi.stubGlobal(
      "fetch",
      mockFetchConMiembros([miembro("m-yo", SUB, "member"), miembro("m-otro", "otro-usuario", "admin")])
    );

    renderApp();
    await irAPantallaMiembros();

    await screen.findByText("Miembro m-yo");
    expect(screen.queryByRole("form", { name: "Agregar miembro" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Desactivar" })).not.toBeInTheDocument();
  });

  it("TC-003: mi Miembro tiene rol admin -> Miembros/Tareas reciben rolUsuarioActual admin", async () => {
    mockMatchMedia(true);
    localStorage.setItem(TOKEN_STORAGE_KEY, jwtFalso(SUB));
    vi.stubGlobal(
      "fetch",
      mockFetchConMiembros([miembro("m-yo", SUB, "admin"), miembro("m-otro", "otro-usuario", "member")])
    );

    renderApp();
    await irAPantallaMiembros();

    await screen.findByText("Miembro m-yo");
    expect(screen.getByRole("form", { name: "Agregar miembro" })).toBeInTheDocument();
  });

  it("TC-004: sin ninguna fila de miembros que coincida con mi usuario_id -> fallback 'member', nunca 'admin'", async () => {
    mockMatchMedia(true);
    localStorage.setItem(TOKEN_STORAGE_KEY, jwtFalso(SUB));
    vi.stubGlobal(
      "fetch",
      mockFetchConMiembros([miembro("m-otro", "otro-usuario-1", "admin"), miembro("m-otro-2", "otro-usuario-2", "admin")])
    );

    renderApp();
    await irAPantallaMiembros();

    await screen.findByText("Miembro m-otro");
    expect(screen.queryByRole("form", { name: "Agregar miembro" })).not.toBeInTheDocument();
  });
});
