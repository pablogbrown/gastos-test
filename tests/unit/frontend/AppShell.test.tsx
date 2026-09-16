import { ThemeProvider } from "@mui/material/styles";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AppNav, GRUPOS_DESKTOP, SECCIONES } from "../../../src/frontend/AppNav";
import { theme } from "../../../src/frontend/theme";

/** Simula `window.matchMedia` para un breakpoint dado, tal como lo
 * consulta `useMediaQuery(theme.breakpoints.up('sm'))` (spec
 * `ui-modernization`, REQ-002). `matches` decide si la media query "ancho
 * >= 600px" es verdadera (desktop) o falsa (mobile). */
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

function renderAppNav() {
  return render(
    <ThemeProvider theme={theme}>
      <AppNav pantalla="inicio" onChange={vi.fn()} />
    </ThemeProvider>
  );
}

describe("AppNav (TC-001, TC-002)", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-001: viewport angosto (< 600px) muestra BottomNavigation con las 7 secciones", () => {
    mockMatchMedia(false);
    renderAppNav();

    const nav = screen.getByRole("navigation", { name: "Navegación" });
    SECCIONES.forEach((seccion) => {
      expect(screen.getByRole("button", { name: seccion.label })).toBeInTheDocument();
    });
    expect(nav.querySelector(".MuiBottomNavigation-root")).not.toBeNull();
    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();
  });

  it("TC-002: viewport ancho (>= 600px) muestra barra superior, no BottomNavigation", () => {
    mockMatchMedia(true);
    renderAppNav();

    // Actualizado por spec `nav-agrupada`, REQ-001/REQ-002: el menú
    // superior desktop ya no es un `tablist` con 9 `tab` planos — pasa a
    // 4 elementos de primer nivel, con "Casa"/"Gastos" desplegando sus
    // pantallas como opciones de menú al hacer clic.
    expect(screen.getByRole("navigation", { name: "Navegación" })).toBeInTheDocument();
    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();

    GRUPOS_DESKTOP.forEach((entrada) => {
      const label = entrada.tipo === "suelta" ? entrada.pantalla : entrada.label;
      const nombre =
        entrada.tipo === "suelta"
          ? new RegExp(SECCIONES.find((s) => s.value === label)!.label)
          : label;
      expect(screen.getByRole("button", { name: nombre })).toBeInTheDocument();
    });

    const grupoCasa = GRUPOS_DESKTOP.find(
      (entrada) => entrada.tipo === "grupo" && entrada.label === "Casa"
    );
    if (grupoCasa && grupoCasa.tipo === "grupo") {
      fireEvent.click(screen.getByRole("button", { name: "Casa" }));
      grupoCasa.pantallas.forEach((value) => {
        const seccion = SECCIONES.find((s) => s.value === value)!;
        expect(
          screen.getByRole("menuitem", { name: new RegExp(seccion.label) })
        ).toBeInTheDocument();
      });
    }

    expect(document.querySelector(".MuiBottomNavigation-root")).toBeNull();
  });
});

/** Spec `nav-agrupada`: menú superior desktop agrupado por categoría —
 * TC-001 a TC-005 tal como los define `spec.md`. Usa `GRUPOS_DESKTOP` en
 * vez de hand-duplicar la agrupación para no divergir de la fuente real. */
describe("AppNav — menú agrupado desktop (spec nav-agrupada)", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function renderCon(pantalla: Parameters<typeof AppNav>[0]["pantalla"], onChange = vi.fn()) {
    render(
      <ThemeProvider theme={theme}>
        <AppNav pantalla={pantalla} onChange={onChange} />
      </ThemeProvider>
    );
    return onChange;
  }

  it("TC-001: desktop muestra exactamente 4 elementos de primer nivel (Inicio, Casa, Gastos, Tareas)", () => {
    mockMatchMedia(true);
    renderCon("inicio");

    expect(GRUPOS_DESKTOP).toHaveLength(4);
    GRUPOS_DESKTOP.forEach((entrada) => {
      const nombre =
        entrada.tipo === "suelta"
          ? new RegExp(SECCIONES.find((s) => s.value === entrada.pantalla)!.label)
          : entrada.label;
      expect(screen.getByRole("button", { name: nombre })).toBeInTheDocument();
    });
    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();
  });

  it('TC-002: clic en "Casa" despliega Miembros/Ranking/Actividad; elegir "Ranking" llama a onChange("ranking") y cierra el menú', () => {
    mockMatchMedia(true);
    const onChange = renderCon("inicio");

    fireEvent.click(screen.getByRole("button", { name: "Casa" }));
    ["Miembros", "Ranking", "Actividad"].forEach((label) => {
      expect(screen.getByRole("menuitem", { name: new RegExp(label) })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("menuitem", { name: /Ranking/ }));

    expect(onChange).toHaveBeenCalledWith("ranking");
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();
  });

  it('TC-003: clic en "Gastos" despliega Gastos/Balance/Tarjetas/Suscripciones', () => {
    mockMatchMedia(true);
    renderCon("inicio");

    fireEvent.click(screen.getByRole("button", { name: "Gastos" }));

    ["Gastos", "Balance", "Tarjetas", "Suscripciones"].forEach((label) => {
      expect(screen.getByRole("menuitem", { name: new RegExp(label) })).toBeInTheDocument();
    });
  });

  it('TC-004: con pantalla="tarjetas" el botón "Gastos" se muestra como grupo activo', () => {
    mockMatchMedia(true);
    renderCon("tarjetas");

    expect(screen.getByRole("button", { name: "Gastos" })).toHaveAttribute(
      "aria-current",
      "true"
    );
    expect(screen.getByRole("button", { name: "Casa" })).not.toHaveAttribute("aria-current");
    expect(
      screen.getByRole("button", { name: new RegExp(SECCIONES[0].label) })
    ).not.toHaveAttribute("aria-current");
  });

  it("TC-005 (control): mobile sigue mostrando las 9 pantallas sin agrupar, sin cambios", () => {
    mockMatchMedia(false);
    renderCon("inicio");

    SECCIONES.forEach((seccion) => {
      expect(screen.getByRole("button", { name: seccion.label })).toBeInTheDocument();
    });
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();
    expect(document.querySelector(".MuiBottomNavigation-root")).not.toBeNull();
  });
});

describe("Theme — BottomNavigationAction (TC-004)", () => {
  beforeEach(() => {
    mockMatchMedia(false);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-004: el tema configura un alto mínimo de al menos 44px para los ítems de navegación", () => {
    const override = theme.components?.MuiBottomNavigationAction?.styleOverrides?.root as
      | { minHeight?: number }
      | undefined;

    expect(override?.minHeight).toBeDefined();
    expect(override!.minHeight!).toBeGreaterThanOrEqual(44);
  });

  it("TC-004: los botones de BottomNavigation renderizados aplican la clase con el mínimo táctil", () => {
    renderAppNav();

    const boton = screen.getByRole("button", { name: SECCIONES[0].label });
    expect(boton.className).toContain("MuiBottomNavigationAction-root");
  });
});
