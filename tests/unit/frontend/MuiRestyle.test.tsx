import { ThemeProvider } from "@mui/material/styles";
import { render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

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
          balance: [],
          tareasPendientes: [],
          tareasCompletadasRecientes: [],
          ranking: [],
        }),
      };
    }
    if (url.includes("/balance")) {
      // Spec `balance-mensual`: `obtenerBalance` ahora agrega
      // `?mes=YYYY-MM` a la URL, así que ya no termina en `/balance`.
      return { ok: true, json: async () => ({ balances: [], transferencias: [] }) };
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
    const { container, findByLabelText } = render(
      conTema(<Gastos casaId={CASA_ID} miembros={[]} />)
    );
    await findByLabelText("Nuevo gasto");
    assertSoloControlesMui(container);
  });

  it("Balance", async () => {
    const { container, findByText } = render(conTema(<Balance casaId={CASA_ID} />));
    await findByText("Transferencias sugeridas");
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
