import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { MantenimientoAutos } from "../../../src/frontend/pages/MantenimientoAutos";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const AUTO_ID = "22222222-2222-2222-2222-222222222222";

function auto(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: AUTO_ID,
    casa_id: CASA_ID,
    marca: "Toyota",
    modelo: "Corolla",
    patente: "AB123CD",
    anio: 2020,
    creado_en: "2026-09-16T10:00:00",
    ...overrides,
  };
}

function itemDeAuto(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    casa_id: CASA_ID,
    nombre: "Cambio de aceite",
    descripcion: null,
    fecha_estimada: null,
    recurrente: false,
    periodicidad: null,
    estado: "pendiente",
    creado_en: "2026-09-16T10:00:00",
    materiales: [],
    auto_id: AUTO_ID,
    ...overrides,
  };
}

describe("MantenimientoAutos", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-006: registrar un auto y cargarle un ítem los muestra agrupados correctamente", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn();
    fetchMock
      // 1. Carga inicial: sin autos.
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      // 2. POST /autos.
      .mockResolvedValueOnce({ ok: true, json: async () => auto() })
      // 3. Recarga tras registrar el auto: listarAutos.
      .mockResolvedValueOnce({ ok: true, json: async () => [auto()] })
      // 4. Recarga: listarItems(casaId, auto.id) — todavía sin ítems.
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      // 5. POST /mantenimiento con auto_id.
      .mockResolvedValueOnce({ ok: true, json: async () => itemDeAuto() })
      // 6. Recarga tras crear el ítem: listarAutos.
      .mockResolvedValueOnce({ ok: true, json: async () => [auto()] })
      // 7. Recarga: listarItems ya con el ítem creado.
      .mockResolvedValueOnce({ ok: true, json: async () => [itemDeAuto()] });
    vi.stubGlobal("fetch", fetchMock);

    render(<MantenimientoAutos casaId={CASA_ID} />);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(screen.getByText("Todavía no hay autos registrados.")).toBeInTheDocument();

    await user.type(screen.getByLabelText("Marca"), "Toyota");
    await user.type(screen.getByLabelText("Modelo"), "Corolla");
    await user.type(screen.getByLabelText("Patente"), "AB123CD");
    await user.type(screen.getByLabelText("Año"), "2020");
    await user.click(screen.getByRole("button", { name: "Registrar auto" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(4));

    const [, crearAutoRequest] = fetchMock.mock.calls[1];
    const cuerpoAuto = JSON.parse(crearAutoRequest.body as string);
    expect(cuerpoAuto).toEqual({
      marca: "Toyota",
      modelo: "Corolla",
      patente: "AB123CD",
      anio: 2020,
    });

    expect(await screen.findByText("Toyota Corolla — AB123CD")).toBeInTheDocument();
    expect(
      screen.getByText("Todavía no hay mantenimiento cargado para este auto.")
    ).toBeInTheDocument();

    await user.type(
      screen.getByLabelText("Nombre", { selector: `#nombre-item-${AUTO_ID}` }),
      "Cambio de aceite"
    );
    await user.click(screen.getByRole("button", { name: "Crear ítem" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(7));

    const [, crearItemRequest] = fetchMock.mock.calls[4];
    const cuerpoItem = JSON.parse(crearItemRequest.body as string);
    expect(cuerpoItem.nombre).toBe("Cambio de aceite");
    expect(cuerpoItem.auto_id).toBe(AUTO_ID);

    // El ítem queda agrupado bajo la sección de su propio auto.
    const seccionAuto = screen.getByRole("region", { name: "Mantenimiento de Toyota Corolla" });
    expect(seccionAuto).toBeInTheDocument();
    await waitFor(() =>
      expect(
        within(seccionAuto).getByText("Cambio de aceite")
      ).toBeInTheDocument()
    );
  });

  it("presionar Enter en el campo Material lo agrega a la lista en vez de enviar el formulario (regresión)", async () => {
    const user = userEvent.setup();
    const itemConMaterial = itemDeAuto({
      materiales: [
        {
          id: "m1",
          item_mantenimiento_id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
          nombre: "Filtro de aire",
          cantidad: 1,
          conseguido: false,
        },
      ],
    });
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: async () => [auto()] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => itemConMaterial })
      .mockResolvedValueOnce({ ok: true, json: async () => [auto()] })
      .mockResolvedValueOnce({ ok: true, json: async () => [itemConMaterial] });
    vi.stubGlobal("fetch", fetchMock);

    render(<MantenimientoAutos casaId={CASA_ID} />);

    await screen.findByText("Toyota Corolla — AB123CD");

    await user.type(
      screen.getByLabelText("Nombre", { selector: `#nombre-item-${AUTO_ID}` }),
      "Cambio de filtro"
    );
    await user.type(screen.getByLabelText("Material"), "Filtro de aire{Enter}");

    // El material queda en la lista pendiente sin haber enviado el
    // formulario todavía (sigue en 2 fetches: autos + items iniciales).
    expect(screen.getByText("Filtro de aire (1)")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(2);

    await user.click(screen.getByRole("button", { name: "Crear ítem" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(5));

    const [, crearItemRequest] = fetchMock.mock.calls[2];
    const cuerpoItem = JSON.parse(crearItemRequest.body as string);
    expect(cuerpoItem.materiales).toEqual([{ nombre: "Filtro de aire", cantidad: 1 }]);
  });

  it("no muestra el mensaje de 'sin autos' mientras carga", () => {
    const fetchMock = vi.fn(() => new Promise(() => {}));
    vi.stubGlobal("fetch", fetchMock);

    render(<MantenimientoAutos casaId={CASA_ID} />);

    expect(screen.getByText("Cargando Mantenimiento Autos...")).toBeInTheDocument();
  });
});
