import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Gastos } from "../../../src/frontend/pages/Gastos";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ADMIN_ID = "22222222-2222-2222-2222-222222222222";
const CATEGORIA_ID = "33333333-3333-3333-3333-333333333333";

const MIEMBROS = [
  {
    id: ADMIN_ID,
    casa_id: CASA_ID,
    nombre: "Administrador",
    identificacion: ADMIN_ID,
    rol: "admin" as const,
    activo: true,
  },
];

function mockFetch() {
  return vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/categorias")) {
      return {
        ok: true,
        json: async () => [{ id: CATEGORIA_ID, casa_id: CASA_ID, nombre: "Supermercado" }],
      };
    }
    if (url.endsWith("/gastos")) {
      return {
        ok: true,
        json: async () => [
          {
            id: "44444444-4444-4444-4444-444444444444",
            casa_id: CASA_ID,
            descripcion: "Compra semanal",
            importe: "100.00",
            fecha: "2026-01-01",
            pagado_por: ADMIN_ID,
            categoria_id: CATEGORIA_ID,
            participantes: [],
          },
        ],
      };
    }
    return { ok: true, json: async () => ({}) };
  });
}

describe("Gastos", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", mockFetch());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("muestra el historial de gastos y el catálogo de categorías", async () => {
    render(<Gastos casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText("Compra semanal")).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Supermercado" })).toBeInTheDocument();
  });

  it("preselecciona 'todos los miembros' y oculta la lista de participantes", async () => {
    render(<Gastos casaId={CASA_ID} miembros={MIEMBROS} />);

    await screen.findByLabelText("Nuevo gasto");
    expect(screen.getByLabelText("Todos los miembros")).toBeChecked();
    expect(screen.queryByLabelText("Participantes")).not.toBeInTheDocument();
  });

  it("muestra un error devuelto por la API al registrar un gasto sin categoría", async () => {
    const fetchMock = mockFetch();
    fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/gastos") && init?.method === "POST") {
        return {
          ok: false,
          status: 400,
          statusText: "Bad Request",
          json: async () => ({ detail: "El gasto debe tener una categoría asignada." }),
        };
      }
      if (url.endsWith("/categorias")) {
        return { ok: true, json: async () => [] };
      }
      if (url.endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} miembros={MIEMBROS} />);
    await screen.findByLabelText("Nuevo gasto");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Descripción"), "Compra");
    await user.type(screen.getByLabelText("Importe"), "100");
    await user.click(screen.getByRole("button", { name: "Registrar gasto" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/categoría/i);
  });

  it("TC-007: envía cuotas en el body cuando el campo Cuotas está completado", async () => {
    const fetchMock = mockFetch();
    let ultimoBodyPost: unknown = null;
    fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/gastos") && init?.method === "POST") {
        ultimoBodyPost = JSON.parse(String(init.body));
        return {
          ok: true,
          status: 201,
          json: async () => ({
            id: "55555555-5555-5555-5555-555555555555",
            casa_id: CASA_ID,
            descripcion: "Heladera (1/3)",
            importe: "40000.00",
            fecha: "2026-09-15",
            pagado_por: ADMIN_ID,
            categoria_id: CATEGORIA_ID,
            participantes: [],
            cuota_grupo_id: "66666666-6666-6666-6666-666666666666",
            cuota_numero: 1,
            cuota_total: 3,
          }),
        };
      }
      if (url.endsWith("/categorias")) {
        return {
          ok: true,
          json: async () => [{ id: CATEGORIA_ID, casa_id: CASA_ID, nombre: "Supermercado" }],
        };
      }
      if (url.endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} miembros={MIEMBROS} />);
    await screen.findByLabelText("Nuevo gasto");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Descripción"), "Heladera");
    await user.type(screen.getByLabelText("Importe"), "120000");
    await user.type(screen.getByLabelText("Cuotas (opcional)"), "3");
    await user.click(screen.getByRole("button", { name: "Registrar gasto" }));

    await waitFor(() => expect(ultimoBodyPost).not.toBeNull());
    expect((ultimoBodyPost as { cuotas: number }).cuotas).toBe(3);
  });

  it("no envía la clave cuotas cuando el campo Cuotas queda vacío", async () => {
    const fetchMock = mockFetch();
    let ultimoBodyPost: unknown = null;
    fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/gastos") && init?.method === "POST") {
        ultimoBodyPost = JSON.parse(String(init.body));
        return {
          ok: true,
          status: 201,
          json: async () => ({
            id: "77777777-7777-7777-7777-777777777777",
            casa_id: CASA_ID,
            descripcion: "Compra",
            importe: "100.00",
            fecha: "2026-01-01",
            pagado_por: ADMIN_ID,
            categoria_id: CATEGORIA_ID,
            participantes: [],
          }),
        };
      }
      if (url.endsWith("/categorias")) {
        return { ok: true, json: async () => [] };
      }
      if (url.endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} miembros={MIEMBROS} />);
    await screen.findByLabelText("Nuevo gasto");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Descripción"), "Compra");
    await user.type(screen.getByLabelText("Importe"), "100");
    await user.click(screen.getByRole("button", { name: "Registrar gasto" }));

    await waitFor(() => expect(ultimoBodyPost).not.toBeNull());
    expect(ultimoBodyPost).not.toHaveProperty("cuotas");
  });

  it("permite seleccionar participantes explícitos cuando se desmarca 'todos'", async () => {
    render(<Gastos casaId={CASA_ID} miembros={MIEMBROS} />);

    await screen.findByLabelText("Nuevo gasto");
    const user = userEvent.setup();
    await user.click(screen.getByLabelText("Todos los miembros"));

    await waitFor(() => expect(screen.getByLabelText("Participantes")).toBeInTheDocument());
    expect(screen.getByText("Administrador")).toBeInTheDocument();
  });
});
