import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Miembros } from "../../../src/frontend/pages/Miembros";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ADMIN_ID = "22222222-2222-2222-2222-222222222222";
const ANA_ID = "33333333-3333-3333-3333-333333333333";

function mockFetchListaMiembros() {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: async () => [
      {
        id: ADMIN_ID,
        casa_id: CASA_ID,
        nombre: "Administrador",
        identificacion: ADMIN_ID,
        rol: "admin",
        activo: true,
      },
      {
        id: ANA_ID,
        casa_id: CASA_ID,
        nombre: "Ana",
        identificacion: "ANA1",
        rol: "member",
        activo: true,
      },
    ],
  });
}

describe("Miembros", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", mockFetchListaMiembros());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("muestra el listado de miembros activos", async () => {
    render(<Miembros casaId={CASA_ID} usuarioId={ADMIN_ID} rolUsuarioActual="admin" />);

    expect(await screen.findByText("Ana")).toBeInTheDocument();
    expect(screen.getByText("Administrador")).toBeInTheDocument();
  });

  it("muestra la acción Desactivar para un Administrador", async () => {
    render(<Miembros casaId={CASA_ID} usuarioId={ADMIN_ID} rolUsuarioActual="admin" />);

    await waitFor(() => expect(screen.getAllByText("Desactivar").length).toBeGreaterThan(0));
  });

  it("oculta la acción Desactivar y el alta para un rol Miembro (TC-006)", async () => {
    render(<Miembros casaId={CASA_ID} usuarioId={ANA_ID} rolUsuarioActual="member" />);

    await screen.findByText("Ana");
    expect(screen.queryByText("Desactivar")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Agregar miembro")).not.toBeInTheDocument();
  });

  it("muestra un error de identificación duplicada devuelto por la API (TC-004)", async () => {
    const fetchMock = mockFetchListaMiembros();
    fetchMock.mockImplementationOnce(async () => ({
      ok: true,
      json: async () => [],
    }));
    fetchMock.mockImplementationOnce(async () => ({
      ok: false,
      status: 400,
      statusText: "Bad Request",
      json: async () => ({ detail: "Ya existe un miembro con identificación 'ANA1'." }),
    }));
    vi.stubGlobal("fetch", fetchMock);

    render(<Miembros casaId={CASA_ID} usuarioId={ADMIN_ID} rolUsuarioActual="admin" />);
    await screen.findByLabelText("Agregar miembro");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Ana");
    await user.type(screen.getByLabelText("Identificación"), "ANA1");
    await user.click(screen.getByRole("button", { name: "Agregar miembro" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/identificación/i);
  });
});
