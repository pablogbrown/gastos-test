import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Balance } from "../../../src/frontend/pages/Balance";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ADMIN_ID = "22222222-2222-2222-2222-222222222222";

function balanceResponse() {
  return {
    totales: [{ moneda: "ARS", total_gastos: "0" }],
    aportes: [{ miembro_id: ADMIN_ID, nombre: "Administrador", total: "0", moneda: "ARS" }],
  };
}

function mockFetch() {
  return vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes("/balance")) {
      return { ok: true, json: async () => balanceResponse() };
    }
    return { ok: true, json: async () => ({}) };
  });
}

describe("Balance", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("preselecciona el selector de mes en el mes actual al renderizar (TC-004)", async () => {
    const fetchMock = mockFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<Balance casaId={CASA_ID} />);

    const mesActual = new Date().toISOString().slice(0, 7);
    const selector = (await screen.findByLabelText("Mes")) as HTMLInputElement;
    expect(selector.value).toBe(mesActual);
  });

  it("consulta el backend con el mes actual al montar", async () => {
    const fetchMock = mockFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<Balance casaId={CASA_ID} />);

    const mesActual = new Date().toISOString().slice(0, 7);
    await screen.findByText("Administrador — Aportó $0");

    const [primeraLlamada] = fetchMock.mock.calls;
    expect(String(primeraLlamada[0])).toContain(`mes=${mesActual}`);
  });

  it("cambiar el selector dispara una nueva consulta con el mes elegido (TC-005)", async () => {
    const fetchMock = mockFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<Balance casaId={CASA_ID} />);
    const selector = await screen.findByLabelText("Mes");
    await screen.findByText("Administrador — Aportó $0");

    const user = userEvent.setup();
    fetchMock.mockClear();
    await user.clear(selector);
    await user.type(selector, "2026-08");

    await screen.findByText("Administrador — Aportó $0");
    const llamadaConMesElegido = fetchMock.mock.calls.some((call) =>
      String(call[0]).includes("mes=2026-08"),
    );
    expect(llamadaConMesElegido).toBe(true);
  });

  it("muestra el total gastado de la casa y el aporte de cada miembro, sin ninguna cifra de deuda ni transferencia sugerida", async () => {
    const ANA_ID = "33333333-3333-3333-3333-333333333333";
    const fetchMock = vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/balance")) {
        return {
          ok: true,
          json: async () => ({
            totales: [
              { moneda: "ARS", total_gastos: "500000" },
              { moneda: "USD", total_gastos: "60" },
            ],
            aportes: [
              { miembro_id: ADMIN_ID, nombre: "Administrador", total: "300000", moneda: "ARS" },
              { miembro_id: ANA_ID, nombre: "Ana", total: "200000", moneda: "ARS" },
              { miembro_id: ADMIN_ID, nombre: "Administrador", total: "0", moneda: "USD" },
              { miembro_id: ANA_ID, nombre: "Ana", total: "60", moneda: "USD" },
            ],
          }),
        };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Balance casaId={CASA_ID} />);

    expect(await screen.findByText("Pesos")).toBeInTheDocument();
    expect(await screen.findByText("Dólares")).toBeInTheDocument();

    expect(screen.getByText("Total gastado: 500000")).toBeInTheDocument();
    expect(screen.getByText("Total gastado: 60")).toBeInTheDocument();

    expect(screen.getByText("Administrador — Aportó $300000")).toBeInTheDocument();
    expect(screen.getByText("Ana — Aportó $200000")).toBeInTheDocument();
    expect(screen.getByText("Administrador — Aportó $0")).toBeInTheDocument();
    expect(screen.getByText("Ana — Aportó $60")).toBeInTheDocument();

    // Ninguna cifra de deuda ni transferencia sugerida (spec `gastos-sin-reparto`).
    expect(screen.queryByText(/le correspond/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/transferencia/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/debe transferir/i)).not.toBeInTheDocument();
  });

  it("sin actividad en USD, solo renderiza la sección Pesos", async () => {
    const fetchMock = mockFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<Balance casaId={CASA_ID} />);

    expect(await screen.findByText("Pesos")).toBeInTheDocument();
    expect(screen.queryByText("Dólares")).not.toBeInTheDocument();
  });
});
