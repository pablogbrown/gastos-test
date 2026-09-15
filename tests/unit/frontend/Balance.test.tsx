import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Balance } from "../../../src/frontend/pages/Balance";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ADMIN_ID = "22222222-2222-2222-2222-222222222222";

function balanceResponse() {
  return {
    balances: [
      { miembro_id: ADMIN_ID, nombre: "Administrador", pago: "0", correspondia: "0", balance: "0" },
    ],
    transferencias: [],
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
    await screen.findByText("Administrador");

    const [primeraLlamada] = fetchMock.mock.calls;
    expect(String(primeraLlamada[0])).toContain(`mes=${mesActual}`);
  });

  it("cambiar el selector dispara una nueva consulta con el mes elegido (TC-005)", async () => {
    const fetchMock = mockFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<Balance casaId={CASA_ID} />);
    const selector = await screen.findByLabelText("Mes");
    await screen.findByText("Administrador");

    const user = userEvent.setup();
    fetchMock.mockClear();
    await user.clear(selector);
    await user.type(selector, "2026-08");

    await screen.findByText("Administrador");
    const llamadaConMesElegido = fetchMock.mock.calls.some((call) =>
      String(call[0]).includes("mes=2026-08"),
    );
    expect(llamadaConMesElegido).toBe(true);
  });

  it("TC-010: con actividad en ambas monedas, renderiza dos secciones separadas sin ningún total combinado", async () => {
    const ANA_ID = "33333333-3333-3333-3333-333333333333";
    const fetchMock = vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/balance")) {
        return {
          ok: true,
          json: async () => ({
            balances: [
              {
                miembro_id: ADMIN_ID,
                nombre: "Administrador",
                pago: "40000",
                correspondia: "20000",
                balance: "20000",
                moneda: "ARS",
              },
              {
                miembro_id: ANA_ID,
                nombre: "Ana",
                pago: "0",
                correspondia: "20000",
                balance: "-20000",
                moneda: "ARS",
              },
              {
                miembro_id: ADMIN_ID,
                nombre: "Administrador",
                pago: "0",
                correspondia: "20",
                balance: "-20",
                moneda: "USD",
              },
              {
                miembro_id: ANA_ID,
                nombre: "Ana",
                pago: "40",
                correspondia: "20",
                balance: "20",
                moneda: "USD",
              },
            ],
            transferencias: [
              { deudor_id: ANA_ID, acreedor_id: ADMIN_ID, monto: "20000", moneda: "ARS" },
              { deudor_id: ADMIN_ID, acreedor_id: ANA_ID, monto: "20", moneda: "USD" },
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

    // Cada sección tiene su propia tabla — el nombre "Administrador"
    // aparece una vez por sección (fila propia), nunca en un total
    // combinado que sume ambas monedas.
    expect(screen.getAllByText("Administrador")).toHaveLength(2);
    expect(screen.getAllByText("Ana")).toHaveLength(2);

    // Ninguna suma/total combinando ambas monedas en pantalla.
    expect(screen.queryByText(/total/i)).not.toBeInTheDocument();
  });

  it("sin actividad en USD, solo renderiza la sección Pesos", async () => {
    const fetchMock = mockFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<Balance casaId={CASA_ID} />);

    expect(await screen.findByText("Pesos")).toBeInTheDocument();
    expect(screen.queryByText("Dólares")).not.toBeInTheDocument();
  });
});
