import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Suscripciones } from "../../../src/frontend/pages/Suscripciones";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const CATEGORIA_ID = "22222222-2222-2222-2222-222222222222";
const ADMIN_ID = "33333333-3333-3333-3333-333333333333";
const ACTIVA_ID = "44444444-4444-4444-4444-444444444444";
const CANCELADA_ID = "55555555-5555-5555-5555-555555555555";

function suscripcion(overrides: Partial<Record<string, unknown>>) {
  return {
    id: ACTIVA_ID,
    casa_id: CASA_ID,
    descripcion: "Netflix",
    importe: "5000.00",
    categoria_id: CATEGORIA_ID,
    pagado_por: ADMIN_ID,
    activa: true,
    ultimo_mes_generado: "2026-09",
    creado_en: "2026-09-15T00:00:00Z",
    ...overrides,
  };
}

function mockFetchListado() {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: async () => [
      suscripcion({ id: ACTIVA_ID, descripcion: "Netflix", activa: true }),
      suscripcion({
        id: CANCELADA_ID,
        descripcion: "Spotify",
        importe: "1000.00",
        activa: false,
      }),
    ],
  });
}

describe("Suscripciones", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", mockFetchListado());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-006: lista activas e inactivas, y ofrece Cancelar solo para la activa (admin)", async () => {
    render(<Suscripciones casaId={CASA_ID} rolUsuarioActual="admin" />);

    expect(await screen.findByText("Netflix")).toBeInTheDocument();
    expect(screen.getByText("Spotify")).toBeInTheDocument();
    expect(screen.getByText("Activa")).toBeInTheDocument();
    expect(screen.getByText("Inactiva")).toBeInTheDocument();

    const botonesCancelar = screen.getAllByRole("button", { name: "Cancelar" });
    expect(botonesCancelar).toHaveLength(1);
  });

  it("oculta la acción Cancelar para un rol Miembro", async () => {
    render(<Suscripciones casaId={CASA_ID} rolUsuarioActual="member" />);

    await screen.findByText("Netflix");
    expect(screen.queryByRole("button", { name: "Cancelar" })).not.toBeInTheDocument();
  });

  it("cancela una suscripción activa y refresca el listado", async () => {
    const fetchMock = mockFetchListado();
    fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes(`/suscripciones/${ACTIVA_ID}`) && init?.method === "PATCH") {
        return {
          ok: true,
          json: async () => suscripcion({ id: ACTIVA_ID, activa: false }),
        };
      }
      return {
        ok: true,
        json: async () => [
          suscripcion({ id: ACTIVA_ID, descripcion: "Netflix", activa: true }),
          suscripcion({
            id: CANCELADA_ID,
            descripcion: "Spotify",
            importe: "1000.00",
            activa: false,
          }),
        ],
      };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Suscripciones casaId={CASA_ID} rolUsuarioActual="admin" />);
    await screen.findByText("Netflix");

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Cancelar" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining(`/suscripciones/${ACTIVA_ID}`),
        expect.objectContaining({ method: "PATCH" })
      )
    );
  });
});
