import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Mantenimiento } from "../../../src/frontend/pages/Mantenimiento";

const CASA_ID = "11111111-1111-1111-1111-111111111111";

function itemPendiente(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    casa_id: CASA_ID,
    nombre: "Poner membrana al techo",
    descripcion: null,
    fecha_estimada: "2026-12-01",
    recurrente: true,
    periodicidad: "anual",
    estado: "pendiente",
    creado_en: "2026-09-16T10:00:00",
    materiales: [
      {
        id: "m1",
        item_mantenimiento_id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        nombre: "Membrana asfáltica",
        cantidad: 2,
        conseguido: false,
      },
      {
        id: "m2",
        item_mantenimiento_id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        nombre: "Silicona",
        cantidad: 1,
        conseguido: false,
      },
    ],
    ...overrides,
  };
}

describe("Mantenimiento", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-009: crear un ítem con materiales agregados lo muestra en el listado con su checklist", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => itemPendiente() })
      .mockResolvedValueOnce({ ok: true, json: async () => [itemPendiente()] });
    vi.stubGlobal("fetch", fetchMock);

    render(<Mantenimiento casaId={CASA_ID} />);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

    await user.type(screen.getByLabelText("Nombre"), "Poner membrana al techo");
    await user.type(screen.getByLabelText("Material"), "Membrana asfáltica");
    await user.clear(screen.getByLabelText("Cantidad"));
    await user.type(screen.getByLabelText("Cantidad"), "2");
    await user.click(screen.getByRole("button", { name: "Agregar material" }));

    await user.type(screen.getByLabelText("Material"), "Silicona");
    await user.click(screen.getByRole("button", { name: "Agregar material" }));

    expect(screen.getByText("Membrana asfáltica (2)")).toBeInTheDocument();
    expect(screen.getByText("Silicona (1)")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Crear ítem" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));

    const [, crearRequest] = fetchMock.mock.calls[1];
    const body = JSON.parse(crearRequest.body as string);
    expect(body.nombre).toBe("Poner membrana al techo");
    expect(body.materiales).toEqual([
      { nombre: "Membrana asfáltica", cantidad: 2 },
      { nombre: "Silicona", cantidad: 1 },
    ]);

    expect(await screen.findByText("Poner membrana al techo")).toBeInTheDocument();
    expect(screen.getByLabelText(/Membrana asfáltica \(2\)/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Silicona \(1\)/)).toBeInTheDocument();
  });

  it("completar un ítem pendiente dispara el PATCH y recarga el listado", async () => {
    const user = userEvent.setup();
    const item = itemPendiente();
    const completado = { ...item, estado: "completado" };
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: async () => [item] })
      .mockResolvedValueOnce({ ok: true, json: async () => completado })
      .mockResolvedValueOnce({ ok: true, json: async () => [completado] });
    vi.stubGlobal("fetch", fetchMock);

    render(<Mantenimiento casaId={CASA_ID} />);

    await screen.findByText("Poner membrana al techo");
    await user.click(screen.getByRole("button", { name: "Completar" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
    expect(await screen.findByText("completado")).toBeInTheDocument();
  });

  it("marcar un material como conseguido dispara el PATCH del material", async () => {
    const user = userEvent.setup();
    const item = itemPendiente();
    const materialConseguido = {
      ...item,
      materiales: item.materiales.map((m) =>
        m.id === "m1" ? { ...m, conseguido: true } : m
      ),
    };
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: async () => [item] })
      .mockResolvedValueOnce({ ok: true, json: async () => item.materiales[0] })
      .mockResolvedValueOnce({ ok: true, json: async () => [materialConseguido] });
    vi.stubGlobal("fetch", fetchMock);

    render(<Mantenimiento casaId={CASA_ID} />);

    await screen.findByText("Poner membrana al techo");
    await user.click(screen.getByRole("checkbox", { name: /Membrana asfáltica/ }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
    const [, patchRequest] = fetchMock.mock.calls[1];
    expect(JSON.parse(patchRequest.body as string)).toEqual({ conseguido: true });
  });
});
