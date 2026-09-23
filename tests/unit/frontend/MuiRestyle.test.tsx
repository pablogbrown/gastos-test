import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import { ThemeProvider } from "@mui/material/styles";
import { render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Spec `perfil-avatar-ui`: Miembros/Ranking ahora renderizan
// `AvatarConAccesorios` (LottieAvatar) — mismo criterio ya establecido
// por `LottieAvatar.test.tsx`/`Miembros.test.tsx`: se mockea `lottie-react`
// para que este smoke test de markup no dependa del efecto de red real
// de `lottie-web`.
vi.mock("lottie-react", () => ({
  Lottie: () => <div data-testid="lottie-mock" />,
}));

import { Balance } from "../../../src/frontend/pages/Balance";
import { CrearCasa } from "../../../src/frontend/pages/CrearCasa";
import { Gastos } from "../../../src/frontend/pages/Gastos";
import { HistorialActividad } from "../../../src/frontend/pages/HistorialActividad";
import { InicioCasa } from "../../../src/frontend/pages/InicioCasa";
import { Miembros } from "../../../src/frontend/pages/Miembros";
import { Ranking } from "../../../src/frontend/pages/Ranking";
import { Tareas } from "../../../src/frontend/pages/Tareas";
import { theme } from "../../../src/frontend/theme";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const USUARIO_ID = "22222222-2222-2222-2222-222222222222";

/** Respuestas vacías/genéricas suficientes para que cada una de las 8
 * pantallas rediseñadas monte sin errores (spec `ui-modernization`,
 * TC-003) — este test no verifica comportamiento de datos (ya cubierto
 * por los tests dedicados de cada pantalla), solo que el markup
 * resultante usa componentes de Material UI. */
function mockFetchGenerico() {
  return vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/inicio")) {
      return {
        ok: true,
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
    if (url.includes("/balance")) {
      // Spec `balance-mensual`: `obtenerBalance` ahora agrega
      // `?mes=YYYY-MM` a la URL, así que ya no termina en `/balance`.
      // Spec `gastos-sin-reparto`: nuevo contrato `{totales, aportes}`.
      return { ok: true, json: async () => ({ totales: [], aportes: [] }) };
    }
    return { ok: true, json: async () => [] };
  });
}

function conTema(children: React.ReactElement) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}

/** Ningún `<button>` ni `<input>`/`<select>` renderizado debe ser un
 * elemento HTML nativo sin estilo (REQ-003): todo control interactivo
 * debe venir de un componente MUI, identificable por su clase
 * `Mui*-root`/`MuiInputBase-*` generada por `@mui/material`. */
function assertSoloControlesMui(container: HTMLElement) {
  const botones = container.querySelectorAll("button");
  botones.forEach((boton) => {
    expect(boton.className).toMatch(/Mui/);
  });

  const inputs = container.querySelectorAll("input");
  inputs.forEach((input) => {
    expect(input.className).toMatch(/Mui/);
  });

  const selects = container.querySelectorAll("select");
  selects.forEach((select) => {
    expect(select.className).toMatch(/Mui/);
  });

  // Al menos un elemento del árbol debe llevar una clase de MUI —
  // confirma que la pantalla efectivamente usa componentes de la
  // librería y no solo controles de formulario sueltos.
  expect(container.querySelector('[class*="Mui"]')).not.toBeNull();
}

describe("TC-003 — las 8 pantallas usan componentes MUI, no HTML nativo sin estilo", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", mockFetchGenerico());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("CrearCasa", () => {
    const { container } = render(conTema(<CrearCasa onCasaCreada={vi.fn()} />));
    assertSoloControlesMui(container);
  });

  it("Miembros", async () => {
    const { container, findByText } = render(
      conTema(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />)
    );
    await findByText("Miembros");
    assertSoloControlesMui(container);
  });

  it("Gastos", async () => {
    const { container, findByLabelText } = render(conTema(<Gastos casaId={CASA_ID} />));
    await findByLabelText("Nuevo gasto");
    assertSoloControlesMui(container);
  });

  it("Balance", async () => {
    const { container, findByText } = render(conTema(<Balance casaId={CASA_ID} />));
    await findByText("Balance");
    assertSoloControlesMui(container);
  });

  it("Tareas", async () => {
    const { container, findByLabelText } = render(
      conTema(<Tareas casaId={CASA_ID} usuarioId={USUARIO_ID} rolUsuarioActual="admin" />)
    );
    await findByLabelText("Crear tarea");
    assertSoloControlesMui(container);
  });

  it("Ranking", async () => {
    const { container, findByText } = render(conTema(<Ranking casaId={CASA_ID} />));
    await findByText("Ranking");
    assertSoloControlesMui(container);
  });

  it("InicioCasa", async () => {
    const { container, findByText } = render(conTema(<InicioCasa casaId={CASA_ID} />));
    await findByText("Todavía no hay miembros activos.");
    assertSoloControlesMui(container);
  });

  it("HistorialActividad", async () => {
    const { container, findByText } = render(
      conTema(<HistorialActividad casaId={CASA_ID} />)
    );
    await findByText("Todavía no hay actividad registrada.");
    assertSoloControlesMui(container);
  });
});

/** Spec `rediseno-ux-ui/sistema-visual`, REQ-001 — tema "Cálido minimal":
 * el tema propio reemplaza el índigo/teal por defecto de MUI y los
 * valores previos de `ui-modernization`, con esquinas generosas y
 * sombra suave de elevación. */
describe("Tema 'Cálido minimal' (TC-001, TC-002)", () => {
  it("TC-001: la paleta y el radio de esquina no coinciden con los valores por defecto de MUI ni con los de ui-modernization", () => {
    expect(theme.palette.primary.main).not.toBe("#3f51b5");
    expect(theme.palette.secondary.main).not.toBe("#00897b");
    expect(theme.shape.borderRadius).not.toBe(4);
    expect(theme.shape.borderRadius).toBeGreaterThanOrEqual(12);
  });

  it("TC-002: un Card renderizado bajo el nuevo tema tiene border-radius >= 12px y una sombra de elevación", () => {
    const { getByTestId } = render(
      conTema(
        <Card data-testid="card-restyled">
          <CardContent>Contenido</CardContent>
        </Card>
      )
    );

    const card = getByTestId("card-restyled");
    const estilo = getComputedStyle(card);

    expect(parseInt(estilo.borderRadius, 10)).toBeGreaterThanOrEqual(12);
    expect(estilo.boxShadow).not.toBe("none");
    expect(estilo.boxShadow).not.toBe("");
  });
});
