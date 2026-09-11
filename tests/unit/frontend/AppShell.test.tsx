import { ThemeProvider } from "@mui/material/styles";
import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AppNav, SECCIONES } from "../../../src/frontend/AppNav";
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

    expect(screen.getByRole("tablist", { name: "Navegación" })).toBeInTheDocument();
    SECCIONES.forEach((seccion) => {
      expect(screen.getByRole("tab", { name: new RegExp(seccion.label) })).toBeInTheDocument();
    });
    expect(document.querySelector(".MuiBottomNavigation-root")).toBeNull();
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
