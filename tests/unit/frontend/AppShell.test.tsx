import { ThemeProvider } from "@mui/material/styles";
import { fireEvent, render, screen, within } from "@testing-library/react";
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

  it("TC-001 (fix nav-mobile-agrupada): viewport angosto (< 600px) muestra BottomNavigation agrupado (Inicio, Casa, Gastos, Tareas) — no las 12 secciones sueltas", () => {
    mockMatchMedia(false);
    renderAppNav();

    const nav = screen.getByRole("navigation", { name: "Navegación" });
    GRUPOS_DESKTOP.forEach((entrada) => {
      const nombre =
        entrada.tipo === "suelta"
          ? new RegExp(SECCIONES.find((s) => s.value === entrada.pantalla)!.label)
          : entrada.label;
      expect(screen.getByRole("button", { name: nombre })).toBeInTheDocument();
    });
    // Una pantalla que hoy vive dentro de un grupo (ej. "Miembros") ya no
    // es un botón suelto en el bottom nav — solo aparece al abrir su grupo.
    expect(screen.queryByRole("button", { name: "Miembros" })).not.toBeInTheDocument();
    expect(nav.querySelector(".MuiBottomNavigation-root")).not.toBeNull();
    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();
  });

  it('TC-001b (fix nav-mobile-agrupada): tocar "Casa" en mobile despliega Miembros/Ranking/Actividad; elegir una llama a onChange y cierra el menú', () => {
    mockMatchMedia(false);
    const onChange = vi.fn();
    render(
      <ThemeProvider theme={theme}>
        <AppNav pantalla="inicio" onChange={onChange} />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByRole("button", { name: "Casa" }));
    ["Miembros", "Ranking", "Actividad"].forEach((label) => {
      expect(screen.getByRole("menuitem", { name: new RegExp(label) })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("menuitem", { name: /Ranking/ }));
    expect(onChange).toHaveBeenCalledWith("ranking");
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();
  });

  it('TC-001c (fix nav-mobile-agrupada): con pantalla="tarjetas" el botón "Gastos" del bottom nav se muestra activo, "Inicio" no', () => {
    mockMatchMedia(false);
    render(
      <ThemeProvider theme={theme}>
        <AppNav pantalla="tarjetas" onChange={vi.fn()} />
      </ThemeProvider>
    );

    const gastos = screen.getByRole("button", { name: "Gastos" });
    const inicio = screen.getByRole("button", { name: "Inicio" });
    const gastosActivo =
      gastos.getAttribute("aria-current") === "true" || gastos.className.includes("Mui-selected");
    expect(gastosActivo).toBe(true);
    expect(inicio.getAttribute("aria-current")).not.toBe("true");
    expect(inicio.className.includes("Mui-selected")).toBe(false);
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

  it('TC-003: clic en "Gastos" despliega Gastos/Balance/Tarjetas/Suscripciones/Préstamos', () => {
    mockMatchMedia(true);
    renderCon("inicio");

    fireEvent.click(screen.getByRole("button", { name: "Gastos" }));

    ["Gastos", "Balance", "Tarjetas", "Suscripciones", "Préstamos"].forEach((label) => {
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

  it("TC-005 (superseded por fix nav-mobile-agrupada): mobile también agrupa por GRUPOS_DESKTOP — ver AppShell.test.tsx TC-001/TC-001b/TC-001c para la cobertura completa del nuevo comportamiento", () => {
    mockMatchMedia(false);
    renderCon("inicio");

    GRUPOS_DESKTOP.forEach((entrada) => {
      const nombre =
        entrada.tipo === "suelta"
          ? new RegExp(SECCIONES.find((s) => s.value === entrada.pantalla)!.label)
          : entrada.label;
      expect(screen.getByRole("button", { name: nombre })).toBeInTheDocument();
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

/** Spec `rediseno-ux-ui/sistema-visual`, REQ-003 — restyle del shell de
 * navegación con el nuevo tema, sin tocar breakpoint ni ruteo. */
describe("AppNav — restyle con el nuevo tema (TC-006, TC-007)", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('TC-006: en mobile, el ítem "Inicio" activo tiene aria-current="true" o el estado selected de MUI activo', () => {
    mockMatchMedia(false);
    renderAppNav();

    const boton = screen.getByRole("button", { name: "Inicio" });
    const tieneAriaCurrent = boton.getAttribute("aria-current") === "true";
    const tieneSelected = boton.className.includes("Mui-selected");
    expect(tieneAriaCurrent || tieneSelected).toBe(true);

    // "Miembros" (fix nav-mobile-agrupada) ya no es un botón suelto en
    // mobile — vive dentro del grupo "Casa", que no debe verse activo.
    const otro = screen.getByRole("button", { name: "Casa" });
    expect(otro.getAttribute("aria-current")).not.toBe("true");
    expect(otro.className.includes("Mui-selected")).toBe(false);
  });

  it("TC-007: en desktop, la agrupación GRUPOS_DESKTOP sigue funcionando sin regresión (grupo activo, submenú, onChange)", () => {
    mockMatchMedia(true);
    const onChange = vi.fn();
    render(
      <ThemeProvider theme={theme}>
        <AppNav pantalla="tarjetas" onChange={onChange} />
      </ThemeProvider>
    );

    expect(screen.getByRole("button", { name: "Gastos" })).toHaveAttribute(
      "aria-current",
      "true"
    );

    fireEvent.click(screen.getByRole("button", { name: "Gastos" }));
    fireEvent.click(screen.getByRole("menuitem", { name: /Balance/ }));
    expect(onChange).toHaveBeenCalledWith("balance");
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();
  });
});

/** Spec `perfil-avatar-ui`, REQ-003/TC-007: "Mi Avatar" vive DENTRO del
 * grupo "Casa" ya existente — nunca un ítem nuevo de primer nivel. El
 * bottom nav mobile sigue mostrando exactamente 4 ítems (Inicio, Casa,
 * Gastos, Tareas), igual que antes de esta spec. */
describe("AppNav — Mi Avatar dentro del grupo Casa (spec perfil-avatar-ui, TC-007)", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-007: el grupo Casa incluye Mi Avatar junto a Miembros/Ranking/Actividad, en desktop y mobile", () => {
    const grupoCasa = GRUPOS_DESKTOP.find(
      (entrada) => entrada.tipo === "grupo" && entrada.label === "Casa"
    );
    expect(grupoCasa && grupoCasa.tipo === "grupo" && grupoCasa.pantallas).toContain("miAvatar");

    mockMatchMedia(true);
    renderAppNav();
    fireEvent.click(screen.getByRole("button", { name: "Casa" }));
    expect(screen.getByRole("menuitem", { name: /Mi Avatar/ })).toBeInTheDocument();
  });

  it("TC-007: el bottom nav mobile sigue mostrando exactamente 4 ítems de primer nivel tras agregar Mi Avatar", () => {
    mockMatchMedia(false);
    renderAppNav();

    expect(GRUPOS_DESKTOP).toHaveLength(4);
    const nav = screen.getByRole("navigation", { name: "Navegación" });
    expect(within(nav).getAllByRole("button").length).toBe(4);
    expect(screen.queryByRole("button", { name: "Mi Avatar" })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Casa" }));
    expect(screen.getByRole("menuitem", { name: /Mi Avatar/ })).toBeInTheDocument();
  });
});
