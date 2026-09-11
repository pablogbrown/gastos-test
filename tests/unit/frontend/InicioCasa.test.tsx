import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InicioCasa } from "../../../src/frontend/pages/InicioCasa";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const USUARIO_ID = "22222222-2222-2222-2222-222222222222";
const ANA_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";

function dashboardVacio() {
  return {
    miembros: [],
    gastosRecientes: [],
    balance: [],
    tareasPendientes: [],
    tareasCompletadasRecientes: [],
    ranking: [],
  };
}

function dashboardConDatos() {
  return {
    miembros: [
      { id: ANA_ID, casa_id: CASA_ID, nombre: "Ana", identificacion: "ANA1", rol: "member", activo: true },
    ],
    gastosRecientes: [
      {
        id: "b1",
        casa_id: CASA_ID,
        descripcion: "Compra semanal",
        importe: "10000.00",
        fecha: "2026-01-01",
        pagado_por: ANA_ID,
        categoria_id: "c1",
        participantes: [],
      },
    ],
    balance: [
      { miembro_id: ANA_ID, nombre: "Ana", pago: "10000.00", correspondia: "10000.00", balance: "0.00" },
    ],
    tareasPendientes: [
      {
        id: "t1",
        casa_id: CASA_ID,
        nombre: "Sacar la basura",
        descripcion: null,
        puntos: 5,
        responsableId: null,
        fechaPrevista: null,
        estado: "pendiente",
        recurrente: false,
        frecuencia: null,
      },
    ],
    tareasCompletadasRecientes: [
      { id: "h1", tarea_id: "t2", miembro_id: ANA_ID, completada_en: "2026-01-02T10:00:00", puntos_obtenidos: 8 },
    ],
    ranking: [{ miembroId: ANA_ID, puntos: 8 }],
  };
}

function mockFetch(dashboard: unknown) {
  return vi.fn().mockResolvedValue({ ok: true, json: async () => dashboard });
}

describe("InicioCasa", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("muestra cada sección vacía sin error para una casa recién creada (TC-002)", async () => {
    vi.stubGlobal("fetch", mockFetch(dashboardVacio()));

    render(<InicioCasa casaId={CASA_ID} usuarioId={USUARIO_ID} />);

    expect(await screen.findByText("Todavía no hay gastos registrados.")).toBeInTheDocument();
    expect(screen.getByText("Todavía no hay miembros activos.")).toBeInTheDocument();
    expect(screen.getByText("No hay tareas pendientes.")).toBeInTheDocument();
    expect(screen.getByText("Todavía no se completó ninguna tarea.")).toBeInTheDocument();
    expect(screen.getByText("Todavía no hay puntos acumulados.")).toBeInTheDocument();
    expect(screen.getByText("Todavía no hay balance para mostrar.")).toBeInTheDocument();
  });

  it("muestra miembros, gastos, tareas y ranking cuando la casa tiene datos (TC-001)", async () => {
    vi.stubGlobal("fetch", mockFetch(dashboardConDatos()));

    render(<InicioCasa casaId={CASA_ID} usuarioId={USUARIO_ID} />);

    expect(await screen.findByText("Ana")).toBeInTheDocument();
    expect(screen.getByText(/Compra semanal/)).toBeInTheDocument();
    expect(screen.getByText(/Sacar la basura/)).toBeInTheDocument();
    expect(screen.getAllByText(/8 pts/).length).toBeGreaterThan(0);
  });

  it("muestra un error devuelto por la API al fallar la carga del dashboard", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: "Not Found",
        json: async () => ({ detail: "La casa no existe." }),
      })
    );

    render(<InicioCasa casaId={CASA_ID} usuarioId={USUARIO_ID} />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/no existe/i);
  });
});
