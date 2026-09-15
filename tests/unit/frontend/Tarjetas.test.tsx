import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Tarjetas } from "../../../src/frontend/pages/Tarjetas";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const TARJETA_ID = "22222222-2222-2222-2222-222222222222";

function tarjeta(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: TARJETA_ID,
    casa_id: CASA_ID,
    miembro_id: "33333333-3333-3333-3333-333333333333",
    banco: "BBVA",
    nombre: "Visa Platinum",
    ultimos_digitos: "1234",
    fecha_cierre_actual: "2026-08-25",
    fecha_vencimiento_actual: "2026-09-07",
    saldo_actual_ars: null,
    saldo_actual_usd: null,
    activa: true,
    creado_en: "2026-09-15T00:00:00Z",
    ...overrides,
  };
}

describe("Tarjetas", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-009: crear una tarjeta desde el formulario la agrega al listado", async () => {
    const user = userEvent.setup();
    let creada = false;

    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/tarjetas") && metodo === "POST") {
          creada = true;
          return { ok: true, status: 201, json: async () => tarjeta() };
        }
        if (url.endsWith("/tarjetas") && metodo === "GET") {
          return { ok: true, status: 200, json: async () => (creada ? [tarjeta()] : []) };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );

    render(<Tarjetas casaId={CASA_ID} />);

    await waitFor(() => expect(screen.queryByText("Visa Platinum")).not.toBeInTheDocument());

    await user.type(screen.getByLabelText("Banco"), "BBVA");
    await user.type(screen.getByLabelText("Nombre"), "Visa Platinum");
    await user.type(screen.getByLabelText("Últimos 4 dígitos"), "1234");
    await user.type(screen.getByLabelText("Fecha de cierre"), "2026-08-25");
    await user.type(screen.getByLabelText("Fecha de vencimiento"), "2026-09-07");
    await user.click(screen.getByRole("button", { name: "Registrar tarjeta" }));

    expect(await screen.findByText("Visa Platinum")).toBeInTheDocument();
    expect(screen.getByText("BBVA")).toBeInTheDocument();
    expect(screen.getByText("•••• 1234")).toBeInTheDocument();
  });

  it("muestra un error devuelto por la API al registrar una tarjeta sin banco", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/tarjetas") && metodo === "POST") {
          return {
            ok: false,
            status: 400,
            statusText: "Bad Request",
            json: async () => ({ detail: "El banco de la tarjeta no puede estar vacío." }),
          };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );
    const user = userEvent.setup();

    render(<Tarjetas casaId={CASA_ID} />);
    await waitFor(() => expect(screen.queryByText("Cargando")).not.toBeInTheDocument());

    await user.type(screen.getByLabelText("Nombre"), "Visa Platinum");
    await user.click(screen.getByRole("button", { name: "Registrar tarjeta" }));

    expect(await screen.findByText(/no puede estar vacío/)).toBeInTheDocument();
  });

  it("TC-010: importar un resumen sube el PDF de inmediato y muestra el resultado sin confirmación", async () => {
    let importado = false;
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/resumen") && metodo === "POST") {
          importado = true;
          return {
            ok: true,
            status: 200,
            json: async () => ({
              gastos_creados: 6,
              cuotas_creadas: 3,
              suscripciones_vinculadas: 1,
              tarjeta: tarjeta(),
            }),
          };
        }
        if (url.endsWith("/tarjetas") && metodo === "GET") {
          return { ok: true, status: 200, json: async () => [tarjeta()] };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );
    const user = userEvent.setup();

    render(<Tarjetas casaId={CASA_ID} />);
    expect(await screen.findByText("Visa Platinum")).toBeInTheDocument();

    const archivo = new File(["contenido-pdf"], "resumen.pdf", { type: "application/pdf" });
    const input = screen.getByLabelText("Importar resumen Visa Platinum");
    // Ningún diálogo de confirmación: seleccionar el archivo ya dispara
    // la subida (REQ-007) — no hay un botón "Confirmar" intermedio que
    // clickear entre esto y la aserción de abajo.
    await user.upload(input, archivo);

    expect(
      await screen.findByText(
        "Resumen importado: 6 gastos creados (3 en cuotas, 1 vinculados a suscripciones)."
      )
    ).toBeInTheDocument();
    expect(importado).toBe(true);
  });

  it("muestra el error devuelto por la API cuando el PDF del resumen no es reconocido", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/resumen") && metodo === "POST") {
          return {
            ok: false,
            status: 422,
            statusText: "Unprocessable Entity",
            json: async () => ({ detail: "El PDF no tiene el formato de resumen reconocido." }),
          };
        }
        if (url.endsWith("/tarjetas") && metodo === "GET") {
          return { ok: true, status: 200, json: async () => [tarjeta()] };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );
    const user = userEvent.setup();

    render(<Tarjetas casaId={CASA_ID} />);
    expect(await screen.findByText("Visa Platinum")).toBeInTheDocument();

    const archivo = new File(["contenido-pdf"], "otro.pdf", { type: "application/pdf" });
    await user.upload(screen.getByLabelText("Importar resumen Visa Platinum"), archivo);

    expect(
      await screen.findByText("El PDF no tiene el formato de resumen reconocido.")
    ).toBeInTheDocument();
  });

  it("elimina una tarjeta y la saca del listado", async () => {
    let eliminada = false;
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (metodo === "DELETE") {
          eliminada = true;
          return { ok: true, status: 204, json: async () => null };
        }
        if (url.endsWith("/tarjetas") && metodo === "GET") {
          return { ok: true, status: 200, json: async () => (eliminada ? [] : [tarjeta()]) };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );
    const user = userEvent.setup();

    render(<Tarjetas casaId={CASA_ID} />);

    expect(await screen.findByText("Visa Platinum")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Eliminar" }));

    await waitFor(() => expect(screen.queryByText("Visa Platinum")).not.toBeInTheDocument());
  });
});
