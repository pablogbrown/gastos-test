import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Tarjetas } from "../../../src/frontend/pages/Tarjetas";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const TARJETA_ID = "22222222-2222-2222-2222-222222222222";

function tarjeta(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: TARJETA_ID,
    casa_id: CASA_ID,
    miembro_id: "33333333-3333-3333-3333-333333333333",
    banco: "BBVA",
    nombre: "Visa Platinum",
    ultimos_digitos: "1234",
    fecha_cierre_actual: "2026-08-25",
    fecha_vencimiento_actual: "2026-09-07",
    saldo_actual_ars: null,
    saldo_actual_usd: null,
    activa: true,
    creado_en: "2026-09-15T00:00:00Z",
    ...overrides,
  };
}

describe("Tarjetas", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-009: crear una tarjeta desde el formulario la agrega al listado", async () => {
    const user = userEvent.setup();
    let creada = false;

    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/tarjetas") && metodo === "POST") {
          creada = true;
          return { ok: true, status: 201, json: async () => tarjeta() };
        }
        if (url.endsWith("/tarjetas") && metodo === "GET") {
          return { ok: true, status: 200, json: async () => (creada ? [tarjeta()] : []) };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );

    render(<Tarjetas casaId={CASA_ID} />);

    await waitFor(() => expect(screen.queryByText("Visa Platinum")).not.toBeInTheDocument());

    await user.type(screen.getByLabelText("Banco"), "BBVA");
    await user.type(screen.getByLabelText("Nombre"), "Visa Platinum");
    await user.type(screen.getByLabelText("Últimos 4 dígitos"), "1234");
    await user.type(screen.getByLabelText("Fecha de cierre"), "2026-08-25");
    await user.type(screen.getByLabelText("Fecha de vencimiento"), "2026-09-07");
    await user.click(screen.getByRole("button", { name: "Registrar tarjeta" }));

    expect(await screen.findByText("Visa Platinum")).toBeInTheDocument();
    expect(screen.getByText("BBVA")).toBeInTheDocument();
    expect(screen.getByText("•••• 1234")).toBeInTheDocument();
  });

  it("muestra un error devuelto por la API al registrar una tarjeta sin banco", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/tarjetas") && metodo === "POST") {
          return {
            ok: false,
            status: 400,
            statusText: "Bad Request",
            json: async () => ({ detail: "El banco de la tarjeta no puede estar vacío." }),
          };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );
    const user = userEvent.setup();

    render(<Tarjetas casaId={CASA_ID} />);
    await waitFor(() => expect(screen.queryByText("Cargando")).not.toBeInTheDocument());

    await user.type(screen.getByLabelText("Nombre"), "Visa Platinum");
    await user.click(screen.getByRole("button", { name: "Registrar tarjeta" }));

    expect(await screen.findByText(/no puede estar vacío/)).toBeInTheDocument();
  });

  it("elimina una tarjeta y la saca del listado", async () => {
    let eliminada = false;
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (metodo === "DELETE") {
          eliminada = true;
          return { ok: true, status: 204, json: async () => null };
        }
        if (url.endsWith("/tarjetas") && metodo === "GET") {
          return { ok: true, status: 200, json: async () => (eliminada ? [] : [tarjeta()]) };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );
    const user = userEvent.setup();

    render(<Tarjetas casaId={CASA_ID} />);

    expect(await screen.findByText("Visa Platinum")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Eliminar" }));

    await waitFor(() => expect(screen.queryByText("Visa Platinum")).not.toBeInTheDocument());
  });
});
