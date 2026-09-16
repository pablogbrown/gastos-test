import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Gastos } from "../../../src/frontend/pages/Gastos";
import * as suscripcionesClient from "../../../src/frontend/api/suscripcionesClient";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ADMIN_ID = "22222222-2222-2222-2222-222222222222";
const CATEGORIA_ID = "33333333-3333-3333-3333-333333333333";

function mockFetch() {
  return vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/categorias")) {
      return {
        ok: true,
        json: async () => [{ id: CATEGORIA_ID, casa_id: CASA_ID, nombre: "Supermercado" }],
      };
    }
    if (url.split("?")[0].endsWith("/gastos")) {
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
    render(<Gastos casaId={CASA_ID} />);

    expect(await screen.findByText("Compra semanal")).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Supermercado" })).toBeInTheDocument();
  });

  it("TC-005: el selector de mes viene preseleccionado en el mes actual", async () => {
    render(<Gastos casaId={CASA_ID} />);

    const mesActual = new Date().toISOString().slice(0, 7);
    const selector = (await screen.findByLabelText("Mes")) as HTMLInputElement;
    expect(selector.value).toBe(mesActual);
  });

  it("TC-004: pide listarGastos con el mes preseleccionado al cargar", async () => {
    const fetchMock = mockFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);
    await screen.findByText("Compra semanal");

    const mesActual = new Date().toISOString().slice(0, 7);
    const llamadaConMesActual = fetchMock.mock.calls.some((call) =>
      String(call[0]).includes(`/gastos?mes=${mesActual}`),
    );
    expect(llamadaConMesActual).toBe(true);
  });

  it("TC-004: cambiar el selector de mes vuelve a pedir el listado con el mes elegido", async () => {
    const fetchMock = mockFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);
    const selector = await screen.findByLabelText("Mes");
    await screen.findByText("Compra semanal");

    const user = userEvent.setup();
    fetchMock.mockClear();
    await user.clear(selector);
    await user.type(selector, "2026-08");

    await waitFor(() => {
      const llamadaConMesElegido = fetchMock.mock.calls.some((call) =>
        String(call[0]).includes("/gastos?mes=2026-08"),
      );
      expect(llamadaConMesElegido).toBe(true);
    });
  });

  it("TC-006: el formulario 'Nuevo gasto' no muestra ningún selector de participantes ni 'Todos los miembros'", async () => {
    render(<Gastos casaId={CASA_ID} />);

    await screen.findByLabelText("Nuevo gasto");
    expect(screen.queryByLabelText("Todos los miembros")).not.toBeInTheDocument();
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
      if (url.split("?")[0].endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);
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
      if (url.split("?")[0].endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);
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
          }),
        };
      }
      if (url.endsWith("/categorias")) {
        return { ok: true, json: async () => [] };
      }
      if (url.split("?")[0].endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);
    await screen.findByLabelText("Nuevo gasto");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Descripción"), "Compra");
    await user.type(screen.getByLabelText("Importe"), "100");
    await user.click(screen.getByRole("button", { name: "Registrar gasto" }));

    await waitFor(() => expect(ultimoBodyPost).not.toBeNull());
    expect(ultimoBodyPost).not.toHaveProperty("cuotas");
  });

  it("TC-007 (spec gastos-suscripcion-mensual): con 'Suscripción mensual' elegido, llama a crearSuscripcion, no a registrarGasto", async () => {
    const fetchMock = mockFetch();
    let seLlamoAlEndpointDeGastosConPost = false;
    fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/gastos") && init?.method === "POST") {
        seLlamoAlEndpointDeGastosConPost = true;
      }
      if (url.endsWith("/categorias")) {
        return {
          ok: true,
          json: async () => [{ id: CATEGORIA_ID, casa_id: CASA_ID, nombre: "Supermercado" }],
        };
      }
      if (url.split("?")[0].endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    const crearSuscripcionSpy = vi
      .spyOn(suscripcionesClient, "crearSuscripcion")
      .mockResolvedValue({
        id: "88888888-8888-8888-8888-888888888888",
        casa_id: CASA_ID,
        descripcion: "Netflix",
        importe: "5000.00",
        categoria_id: CATEGORIA_ID,
        pagado_por: ADMIN_ID,
        activa: true,
        ultimo_mes_generado: "2026-09",
        creado_en: "2026-09-15T00:00:00Z",
      });

    render(<Gastos casaId={CASA_ID} />);
    await screen.findByLabelText("Nuevo gasto");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Descripción"), "Netflix");
    await user.type(screen.getByLabelText("Importe"), "5000");
    await user.selectOptions(screen.getByLabelText("Tipo de gasto"), "suscripcion");
    await user.click(screen.getByRole("button", { name: "Registrar gasto" }));

    await waitFor(() => expect(crearSuscripcionSpy).toHaveBeenCalledTimes(1));
    expect(crearSuscripcionSpy).toHaveBeenCalledWith(
      CASA_ID,
      expect.objectContaining({ descripcion: "Netflix", importe: "5000" })
    );
    expect(seLlamoAlEndpointDeGastosConPost).toBe(false);

    crearSuscripcionSpy.mockRestore();
  });

  it("oculta el campo Cuotas cuando el tipo es Suscripción mensual", async () => {
    render(<Gastos casaId={CASA_ID} />);

    await screen.findByLabelText("Nuevo gasto");
    const user = userEvent.setup();
    await user.selectOptions(screen.getByLabelText("Tipo de gasto"), "suscripcion");

    expect(screen.queryByLabelText("Cuotas (opcional)")).not.toBeInTheDocument();
  });

  it("TC-009: con Moneda en USD, el body enviado a registrarGasto incluye moneda: 'USD'", async () => {
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
            id: "99999999-9999-9999-9999-999999999999",
            casa_id: CASA_ID,
            descripcion: "Compra en dólares",
            importe: "20.00",
            fecha: "2026-01-01",
            pagado_por: ADMIN_ID,
            categoria_id: CATEGORIA_ID,
            moneda: "USD",
          }),
        };
      }
      if (url.endsWith("/categorias")) {
        return {
          ok: true,
          json: async () => [{ id: CATEGORIA_ID, casa_id: CASA_ID, nombre: "Supermercado" }],
        };
      }
      if (url.split("?")[0].endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);
    await screen.findByLabelText("Nuevo gasto");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Descripción"), "Compra en dólares");
    await user.type(screen.getByLabelText("Importe"), "20");
    await user.selectOptions(screen.getByLabelText("Moneda"), "USD");
    await user.click(screen.getByRole("button", { name: "Registrar gasto" }));

    await waitFor(() => expect(ultimoBodyPost).not.toBeNull());
    expect((ultimoBodyPost as { moneda: string }).moneda).toBe("USD");
  });

  it("no fuerza moneda: 'ARS' explícito en el body cuando Moneda queda en el default", async () => {
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
            id: "10101010-1010-1010-1010-101010101010",
            casa_id: CASA_ID,
            descripcion: "Compra",
            importe: "100.00",
            fecha: "2026-01-01",
            pagado_por: ADMIN_ID,
            categoria_id: CATEGORIA_ID,
            moneda: "ARS",
          }),
        };
      }
      if (url.endsWith("/categorias")) {
        return { ok: true, json: async () => [] };
      }
      if (url.split("?")[0].endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);
    await screen.findByLabelText("Nuevo gasto");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Descripción"), "Compra");
    await user.type(screen.getByLabelText("Importe"), "100");
    await user.click(screen.getByRole("button", { name: "Registrar gasto" }));

    await waitFor(() => expect(ultimoBodyPost).not.toBeNull());
    expect(ultimoBodyPost).not.toHaveProperty("moneda");
  });

  it("el selector Moneda viene preseleccionado en ARS", async () => {
    render(<Gastos casaId={CASA_ID} />);

    const selector = (await screen.findByLabelText("Moneda")) as HTMLSelectElement;
    expect(selector.value).toBe("ARS");
  });

  it("el selector Estado viene preseleccionado en Pagado", async () => {
    render(<Gastos casaId={CASA_ID} />);

    const selector = (await screen.findByLabelText("Estado")) as HTMLSelectElement;
    expect(selector.value).toBe("pagado");
  });

  it("TC-009: con Estado en 'A pagar', el body enviado incluye estado: 'a_pagar'", async () => {
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
            id: "12121212-1212-1212-1212-121212121212",
            casa_id: CASA_ID,
            descripcion: "Cuota futura",
            importe: "20.00",
            fecha: "2026-01-01",
            pagado_por: ADMIN_ID,
            categoria_id: CATEGORIA_ID,
            moneda: "ARS",
            estado: "a_pagar",
          }),
        };
      }
      if (url.endsWith("/categorias")) {
        return {
          ok: true,
          json: async () => [{ id: CATEGORIA_ID, casa_id: CASA_ID, nombre: "Supermercado" }],
        };
      }
      if (url.split("?")[0].endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);
    await screen.findByLabelText("Nuevo gasto");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Descripción"), "Cuota futura");
    await user.type(screen.getByLabelText("Importe"), "20");
    await user.selectOptions(screen.getByLabelText("Estado"), "a_pagar");
    await user.click(screen.getByRole("button", { name: "Registrar gasto" }));

    await waitFor(() => expect(ultimoBodyPost).not.toBeNull());
    expect((ultimoBodyPost as { estado: string }).estado).toBe("a_pagar");
  });

  it("no fuerza estado: 'pagado' explícito en el body cuando Estado queda en el default", async () => {
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
            id: "13131313-1313-1313-1313-131313131313",
            casa_id: CASA_ID,
            descripcion: "Compra",
            importe: "100.00",
            fecha: "2026-01-01",
            pagado_por: ADMIN_ID,
            categoria_id: CATEGORIA_ID,
            moneda: "ARS",
            estado: "pagado",
          }),
        };
      }
      if (url.endsWith("/categorias")) {
        return { ok: true, json: async () => [] };
      }
      if (url.split("?")[0].endsWith("/gastos")) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);
    await screen.findByLabelText("Nuevo gasto");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Descripción"), "Compra");
    await user.type(screen.getByLabelText("Importe"), "100");
    await user.click(screen.getByRole("button", { name: "Registrar gasto" }));

    await waitFor(() => expect(ultimoBodyPost).not.toBeNull());
    expect(ultimoBodyPost).not.toHaveProperty("estado");
  });

  it("TC-010: un clic en el chip de estado llama a la API de actualización y el chip pasa a Pagado", async () => {
    // Mock con estado mutable: el PATCH actualiza `estadoActual`, y el
    // siguiente GET (disparado por `cargar()` tras el PATCH) devuelve
    // ese valor ya actualizado -- imprescindible para probar el
    // refresco real de TC-010, no solo la llamada al PATCH.
    let estadoActual: "pagado" | "a_pagar" = "a_pagar";
    const fetchMock = vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/categorias")) {
        return { ok: true, json: async () => [] };
      }
      if (/\/gastos\/[^/]+$/.test(url) && init?.method === "PATCH") {
        estadoActual = JSON.parse(String(init.body)).estado;
        return {
          ok: true,
          json: async () => ({
            id: "44444444-4444-4444-4444-444444444444",
            casa_id: CASA_ID,
            descripcion: "Compra semanal",
            importe: "100.00",
            fecha: "2026-01-01",
            pagado_por: ADMIN_ID,
            categoria_id: CATEGORIA_ID,
            moneda: "ARS",
            estado: estadoActual,
          }),
        };
      }
      if (url.split("?")[0].endsWith("/gastos")) {
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
              moneda: "ARS",
              estado: estadoActual,
            },
          ],
        };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);

    await screen.findByText("Compra semanal");
    // El selector "Estado" del formulario tambien renderiza un <option>
    // con el mismo texto "A pagar" -- se apunta explicitamente al chip
    // clickeable (role="button") de la fila del listado para no
    // ambiguar con esa opcion.
    const chip = screen.getByRole("button", { name: "A pagar" });
    const user = userEvent.setup();
    await user.click(chip);

    expect(await screen.findByRole("button", { name: "Pagado" })).toBeInTheDocument();
    const patchCall = fetchMock.mock.calls.find(
      ([, init]) => (init as RequestInit | undefined)?.method === "PATCH"
    );
    expect(patchCall).toBeDefined();
    expect(JSON.parse(String((patchCall![1] as RequestInit).body))).toEqual({
      estado: "pagado",
    });
  });

  it("muestra el importe con prefijo US$ para un gasto en dólares, $ para uno en pesos", async () => {
    const fetchMock = vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/categorias")) {
        return { ok: true, json: async () => [] };
      }
      if (url.split("?")[0].endsWith("/gastos")) {
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
              moneda: "ARS",
            },
            {
              id: "55555555-5555-5555-5555-555555555555",
              casa_id: CASA_ID,
              descripcion: "Compra en dólares",
              importe: "20.00",
              fecha: "2026-01-02",
              pagado_por: ADMIN_ID,
              categoria_id: CATEGORIA_ID,
              moneda: "USD",
            },
          ],
        };
      }
      return { ok: true, json: async () => ({}) };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<Gastos casaId={CASA_ID} />);

    expect(await screen.findByText("$100.00")).toBeInTheDocument();
    expect(await screen.findByText("US$20.00")).toBeInTheDocument();
  });
});
