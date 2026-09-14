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

  it("permite seleccionar participantes explícitos cuando se desmarca 'todos'", async () => {
    render(<Gastos casaId={CASA_ID} miembros={MIEMBROS} />);

    await screen.findByLabelText("Nuevo gasto");
    const user = userEvent.setup();
    await user.click(screen.getByLabelText("Todos los miembros"));

    await waitFor(() => expect(screen.getByLabelText("Participantes")).toBeInTheDocument());
    expect(screen.getByText("Administrador")).toBeInTheDocument();
  });
});
