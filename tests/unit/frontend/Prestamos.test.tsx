import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Prestamos } from "../../../src/frontend/pages/Prestamos";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const PRESTAMO_ID = "22222222-2222-2222-2222-222222222222";
const ADMIN_ID = "33333333-3333-3333-3333-333333333333";
const MACA_ID = "44444444-4444-4444-4444-444444444444";

const MIEMBROS = [
  {
    id: ADMIN_ID,
    usuario_id: "usuario-admin",
    casa_id: CASA_ID,
    nombre: "Pablo",
    identificacion: "P-1",
    rol: "admin" as const,
    activo: true,
  },
  {
    id: MACA_ID,
    usuario_id: "usuario-maca",
    casa_id: CASA_ID,
    nombre: "Maca",
    identificacion: "P-2",
    rol: "member" as const,
    activo: true,
  },
];

function prestamo(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: PRESTAMO_ID,
    casa_id: CASA_ID,
    prestamista_id: ADMIN_ID,
    deudor_id: MACA_ID,
    importe: "50000.00",
    moneda: "ARS",
    descripcion: "Alquiler del auto",
    fecha: "2026-09-01",
    estado: "pendiente",
    creado_en: "2026-09-16T00:00:00Z",
    // Spec `prestamos-confirmacion-mutua`: por default, en estos tests
    // pre-existentes (que ejercitan el ciclo pagado/pendiente ya
    // confirmado), ambas partes ya confirmaron — así el chip clickeable
    // de estado sigue apareciendo sin cambios.
    confirmado_prestamista: true,
    confirmado_deudor: true,
    estado_confirmacion: "confirmado",
    ...overrides,
  };
}

describe("Prestamos", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-007: crear un préstamo desde el formulario lo agrega al listado", async () => {
    const user = userEvent.setup();
    let creado = false;

    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/prestamos") && metodo === "POST") {
          creado = true;
          const body = JSON.parse(String(init?.body));
          expect(body.prestamista_id).toBe(ADMIN_ID);
          expect(body.deudor_id).toBe(MACA_ID);
          expect(body.importe).toBe("50000");
          expect(body.fecha).toBe("2026-09-01");
          return { ok: true, status: 201, json: async () => prestamo() };
        }
        if (url.endsWith("/prestamos") && metodo === "GET") {
          return { ok: true, status: 200, json: async () => (creado ? [prestamo()] : []) };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );

    render(<Prestamos casaId={CASA_ID} miembros={MIEMBROS} miembroIdActual={ADMIN_ID} />);

    await waitFor(() => expect(screen.queryByText("Alquiler del auto")).not.toBeInTheDocument());

    await user.selectOptions(screen.getByLabelText("Prestamista"), ADMIN_ID);
    await user.selectOptions(screen.getByLabelText("Deudor"), MACA_ID);
    await user.type(screen.getByLabelText("Importe"), "50000");
    await user.type(screen.getByLabelText("Fecha"), "2026-09-01");
    await user.type(screen.getByLabelText("Descripción (opcional)"), "Alquiler del auto");
    await user.click(screen.getByRole("button", { name: "Registrar préstamo" }));

    expect(await screen.findByText("Alquiler del auto")).toBeInTheDocument();
    // "Pablo"/"Maca" también aparecen como <option> en los selects — se
    // acota la búsqueda a la tabla de listado para evitar la ambigüedad
    // (mismo criterio que [FRONP-01] documenta para un Chip vs. un
    // `<Select native>` que comparten texto visible).
    const tabla = screen.getByRole("table", { name: "Listado de préstamos" });
    expect(within(tabla).getByText("Pablo")).toBeInTheDocument();
    expect(within(tabla).getByText("Maca")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Pendiente" })).toBeInTheDocument();
  });

  it("TC-008: un clic en el chip de estado cambia de Pendiente a Pagado", async () => {
    const user = userEvent.setup();
    let estadoActual = "pendiente";

    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/prestamos") && metodo === "GET") {
          return { ok: true, status: 200, json: async () => [prestamo({ estado: estadoActual })] };
        }
        if (url.includes(`/prestamos/${PRESTAMO_ID}`) && metodo === "PATCH") {
          const body = JSON.parse(String(init?.body));
          estadoActual = body.estado;
          return { ok: true, status: 200, json: async () => prestamo({ estado: estadoActual }) };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );

    render(<Prestamos casaId={CASA_ID} miembros={MIEMBROS} miembroIdActual={ADMIN_ID} />);

    const chip = await screen.findByRole("button", { name: "Pendiente" });
    await user.click(chip);

    expect(await screen.findByRole("button", { name: "Pagado" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Pendiente" })).not.toBeInTheDocument();
  });

  it("muestra un error devuelto por la API al registrar un préstamo inválido", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/prestamos") && metodo === "POST") {
          return {
            ok: false,
            status: 400,
            statusText: "Bad Request",
            json: async () => ({
              detail: "El prestamista y el deudor no pueden ser el mismo miembro.",
            }),
          };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );

    const user = userEvent.setup();
    render(<Prestamos casaId={CASA_ID} miembros={MIEMBROS} miembroIdActual={ADMIN_ID} />);

    await user.selectOptions(screen.getByLabelText("Prestamista"), ADMIN_ID);
    await user.selectOptions(screen.getByLabelText("Deudor"), ADMIN_ID);
    await user.type(screen.getByLabelText("Importe"), "1000");
    await user.type(screen.getByLabelText("Fecha"), "2026-09-01");
    await user.click(screen.getByRole("button", { name: "Registrar préstamo" }));

    expect(
      await screen.findByText("El prestamista y el deudor no pueden ser el mismo miembro.")
    ).toBeInTheDocument();
  });

  it("TC-008: un préstamo pendiente de confirmación se ve marcado como tal para un miembro al que no le toca confirmar", async () => {
    const BRUNO_ID = "55555555-5555-5555-5555-555555555555";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async () => ({
        ok: true,
        status: 200,
        json: async () => [
          prestamo({
            confirmado_prestamista: true,
            confirmado_deudor: null,
            estado_confirmacion: "pendiente_confirmacion",
          }),
        ],
      }))
    );

    // Bruno no es ni el prestamista ni el deudor de este préstamo — ve
    // el chip informativo, nunca los botones de acción.
    render(<Prestamos casaId={CASA_ID} miembros={MIEMBROS} miembroIdActual={BRUNO_ID} />);

    expect(await screen.findByText("Pendiente de confirmación")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Rechazar" })).not.toBeInTheDocument();
  });

  it("TC-009: solo la parte a la que le toca confirmar ve los botones Confirmar/Rechazar", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async () => ({
        ok: true,
        status: 200,
        json: async () => [
          prestamo({
            confirmado_prestamista: true,
            confirmado_deudor: null,
            estado_confirmacion: "pendiente_confirmacion",
          }),
        ],
      }))
    );

    // Maca es la deudora y su campo de confirmación todavía está en
    // null: le toca confirmar/rechazar.
    render(<Prestamos casaId={CASA_ID} miembros={MIEMBROS} miembroIdActual={MACA_ID} />);

    expect(await screen.findByRole("button", { name: "Confirmar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Rechazar" })).toBeInTheDocument();
    expect(screen.queryByText("Pendiente de confirmación")).not.toBeInTheDocument();
  });

  it("TC-009: el prestamista que ya confirmó no ve los botones en su propia fila", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async () => ({
        ok: true,
        status: 200,
        json: async () => [
          prestamo({
            confirmado_prestamista: true,
            confirmado_deudor: null,
            estado_confirmacion: "pendiente_confirmacion",
          }),
        ],
      }))
    );

    // Admin (prestamista) ya confirmó automáticamente al registrar —
    // ve el chip informativo, no los botones, aunque sea parte del
    // préstamo.
    render(<Prestamos casaId={CASA_ID} miembros={MIEMBROS} miembroIdActual={ADMIN_ID} />);

    expect(await screen.findByText("Pendiente de confirmación")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
  });

  it("confirmar un préstamo llama al endpoint de confirmación y refresca el listado", async () => {
    const user = userEvent.setup();
    let confirmado = false;

    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        const metodo = init?.method ?? "GET";
        if (url.endsWith("/confirmacion") && metodo === "PATCH") {
          const body = JSON.parse(String(init?.body));
          expect(body.confirma).toBe(true);
          confirmado = true;
          return {
            ok: true,
            status: 200,
            json: async () => prestamo({ confirmado_deudor: true, estado_confirmacion: "confirmado" }),
          };
        }
        if (url.endsWith("/prestamos") && metodo === "GET") {
          return {
            ok: true,
            status: 200,
            json: async () => [
              prestamo(
                confirmado
                  ? { confirmado_deudor: true, estado_confirmacion: "confirmado" }
                  : {
                      confirmado_prestamista: true,
                      confirmado_deudor: null,
                      estado_confirmacion: "pendiente_confirmacion",
                    }
              ),
            ],
          };
        }
        return { ok: true, status: 200, json: async () => [] };
      })
    );

    render(<Prestamos casaId={CASA_ID} miembros={MIEMBROS} miembroIdActual={MACA_ID} />);

    await user.click(await screen.findByRole("button", { name: "Confirmar" }));

    // El préstamo mockeado nace con `estado: "pendiente"` (sin cambios) —
    // una vez confirmado por ambas partes, vuelve a mostrar el chip
    // clickeable de pagado/pendiente en vez de los botones de acción.
    expect(await screen.findByRole("button", { name: "Pendiente" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
  });

  it("un préstamo rechazado se ve con el chip 'Rechazado', sin acciones", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async () => ({
        ok: true,
        status: 200,
        json: async () => [
          prestamo({
            confirmado_prestamista: true,
            confirmado_deudor: false,
            estado_confirmacion: "rechazado",
          }),
        ],
      }))
    );

    render(<Prestamos casaId={CASA_ID} miembros={MIEMBROS} miembroIdActual={MACA_ID} />);

    expect(await screen.findByText("Rechazado")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Rechazar" })).not.toBeInTheDocument();
  });
});
