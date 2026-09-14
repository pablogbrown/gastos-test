import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SelectorCasas } from "../../../src/frontend/pages/SelectorCasas";

const CASA_1 = {
  id: "11111111-1111-1111-1111-111111111111",
  nombre: "Casa del centro",
  creado_en: "2026-01-01T00:00:00",
  miembros: [],
};

const CASA_2 = {
  id: "22222222-2222-2222-2222-222222222222",
  nombre: "Casa de la playa",
  creado_en: "2026-01-02T00:00:00",
  miembros: [],
};

describe("SelectorCasas (TC-005)", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("un usuario con 2 casas ve el selector y puede elegir una", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => [CASA_1, CASA_2] }));
    const onCasaElegida = vi.fn();

    render(<SelectorCasas onCasaElegida={onCasaElegida} />);

    expect(await screen.findByText("Casa del centro")).toBeInTheDocument();
    expect(screen.getByText("Casa de la playa")).toBeInTheDocument();

    const user = userEvent.setup();
    await user.click(screen.getByText("Casa de la playa"));

    expect(onCasaElegida).toHaveBeenCalledWith(CASA_2);
  });

  it("sin casas, ofrece 'Crear nueva casa' en vez de una lista vacía", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => [] }));

    render(<SelectorCasas onCasaElegida={vi.fn()} />);

    expect(await screen.findByText("Todavía no pertenecés a ninguna casa.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Crear nueva casa" })).toBeInTheDocument();
  });

  it("'Crear nueva casa' muestra el formulario de CrearCasa", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => [] }));

    render(<SelectorCasas onCasaElegida={vi.fn()} />);
    await screen.findByText("Todavía no pertenecés a ninguna casa.");

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Crear nueva casa" }));

    expect(await screen.findByLabelText("Crear casa")).toBeInTheDocument();
  });

  it("muestra un error devuelto por la API al fallar la carga de casas", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: "Unauthorized",
        json: async () => ({ detail: "No autenticado." }),
      })
    );

    render(<SelectorCasas onCasaElegida={vi.fn()} />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/no autenticado/i);
  });
});
