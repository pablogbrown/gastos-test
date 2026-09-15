import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Miembros } from "../../../src/frontend/pages/Miembros";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ADMIN_ID = "22222222-2222-2222-2222-222222222222";
const ANA_ID = "33333333-3333-3333-3333-333333333333";

const PENDIENTE_ID = "44444444-4444-4444-4444-444444444444";

function mockFetchListaMiembros() {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: async () => [
      {
        id: ADMIN_ID,
        usuario_id: ADMIN_ID,
        casa_id: CASA_ID,
        nombre: "Administrador",
        identificacion: ADMIN_ID,
        rol: "admin",
        activo: true,
      },
      {
        id: ANA_ID,
        usuario_id: ANA_ID,
        casa_id: CASA_ID,
        nombre: "Ana",
        identificacion: "ANA1",
        rol: "member",
        activo: true,
      },
    ],
  });
}

function mockFetchListaConMiembroPendiente() {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: async () => [
      {
        id: ADMIN_ID,
        usuario_id: ADMIN_ID,
        casa_id: CASA_ID,
        nombre: "Administrador",
        identificacion: ADMIN_ID,
        rol: "admin",
        activo: true,
      },
      {
        id: PENDIENTE_ID,
        usuario_id: null,
        casa_id: CASA_ID,
        nombre: "Invitado Pendiente",
        identificacion: "PEND1",
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
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    expect(await screen.findByText("Ana")).toBeInTheDocument();
    expect(screen.getByText("Administrador")).toBeInTheDocument();
  });

  it("muestra la acción Desactivar para un Administrador", async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    await waitFor(() => expect(screen.getAllByText("Desactivar").length).toBeGreaterThan(0));
  });

  it("oculta la acción Desactivar y el alta para un rol Miembro (TC-006)", async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="member" />);

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

    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);
    await screen.findByLabelText("Agregar miembro");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Ana");
    await user.type(screen.getByLabelText("Identificación"), "ANA1");
    await user.type(screen.getByLabelText("Email"), "ana@example.com");
    await user.click(screen.getByRole("button", { name: "Agregar miembro" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/identificación/i);
  });

  it('muestra "Pendiente" y oculta Desactivar para una membresía sin usuario_id (TC-007)', async () => {
    vi.stubGlobal("fetch", mockFetchListaConMiembroPendiente());

    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    const nombreCelda = await screen.findByText("Invitado Pendiente");
    const filaPendiente = nombreCelda.closest("tr") as HTMLElement;

    expect(within(filaPendiente).getByText("Pendiente")).toBeInTheDocument();
    expect(within(filaPendiente).queryByText("Activo")).not.toBeInTheDocument();
    expect(within(filaPendiente).queryByText("Inactivo")).not.toBeInTheDocument();
    expect(within(filaPendiente).queryByText("Desactivar")).not.toBeInTheDocument();
  });

  it('sigue mostrando Activo/Inactivo y Desactivar para una membresía vinculada (TC-008)', async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    await screen.findByText("Ana");
    expect(screen.getAllByText("Activo").length).toBeGreaterThan(0);
    expect(screen.queryByText("Pendiente")).not.toBeInTheDocument();
    expect(screen.getAllByText("Desactivar").length).toBeGreaterThan(0);
  });

  it("envía el email del usuario a vincular al agregar un miembro (regresión: 'field required')", async () => {
    const fetchMock = mockFetchListaMiembros();
    fetchMock.mockImplementationOnce(async () => ({
      ok: true,
      json: async () => [],
    }));
    fetchMock.mockImplementationOnce(async () => ({
      ok: true,
      json: async () => ({
        id: "55555555-5555-5555-5555-555555555555",
        casa_id: CASA_ID,
        nombre: "Pablo",
        identificacion: "papá",
        rol: "member",
        activo: true,
      }),
    }));
    vi.stubGlobal("fetch", fetchMock);

    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);
    await screen.findByLabelText("Agregar miembro");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Pablo");
    await user.type(screen.getByLabelText("Identificación"), "papá");
    await user.type(screen.getByLabelText("Email"), "pablo@example.com");
    await user.click(screen.getByRole("button", { name: "Agregar miembro" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
    const [, altaRequest] = fetchMock.mock.calls[1];
    const body = JSON.parse((altaRequest as RequestInit).body as string);
    expect(body).toEqual({ nombre: "Pablo", identificacion: "papá", email: "pablo@example.com" });
  });
});
