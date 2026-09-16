import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InicioCasa } from "../../../src/frontend/pages/InicioCasa";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ANA_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";

const MIEMBROS = [
  { id: ANA_ID, casa_id: CASA_ID, nombre: "Ana", identificacion: "ANA1", rol: "member", activo: true },
];

function dashboardVacio() {
  return {
    miembros: [],
    gastosRecientes: [],
    balance: { totales: [{ moneda: "ARS", total_gastos: "0" }], aportes: [] },
    tareasPendientes: [],
    tareasCompletadasRecientes: [],
    ranking: [],
    tarjetasConAlerta: [],
    mantenimientoConAlerta: [],
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
      },
    ],
    balance: {
      totales: [{ moneda: "ARS", total_gastos: "10000.00" }],
      aportes: [{ miembro_id: ANA_ID, nombre: "Ana", total: "10000.00", moneda: "ARS" }],
    },
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
    tarjetasConAlerta: [],
    mantenimientoConAlerta: [],
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

    render(<InicioCasa casaId={CASA_ID} miembros={[]} />);

    expect(await screen.findByText("Todavía no hay gastos registrados.")).toBeInTheDocument();
    expect(screen.getByText("Todavía no hay miembros activos.")).toBeInTheDocument();
    expect(screen.getByText("No hay tareas pendientes.")).toBeInTheDocument();
    expect(screen.getByText("Todavía no se completó ninguna tarea.")).toBeInTheDocument();
    expect(screen.getByText("Todavía no hay puntos acumulados.")).toBeInTheDocument();
    expect(screen.getByText("Todavía no hay balance para mostrar.")).toBeInTheDocument();
  });

  it("muestra miembros, gastos, tareas y ranking cuando la casa tiene datos (TC-001)", async () => {
    vi.stubGlobal("fetch", mockFetch(dashboardConDatos()));

    render(<InicioCasa casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText("Ana")).toBeInTheDocument();
    expect(screen.getByText(/Compra semanal/)).toBeInTheDocument();
    expect(screen.getByText(/Sacar la basura/)).toBeInTheDocument();
    expect(screen.getAllByText(/8 pts/).length).toBeGreaterThan(0);
  });

  it("TC-007: la sección Balance muestra el nuevo total de la casa en ARS, sin ninguna cifra de deuda por miembro", async () => {
    vi.stubGlobal("fetch", mockFetch(dashboardConDatos()));

    render(<InicioCasa casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText("Total gastado: $10000.00")).toBeInTheDocument();
    expect(screen.queryByText("Ana: 0.00")).not.toBeInTheDocument();
  });

  it('"Tareas completadas recientes" muestra el nombre del miembro, no su UUID (TC-003)', async () => {
    vi.stubGlobal("fetch", mockFetch(dashboardConDatos()));

    render(<InicioCasa casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText(/Ana completó una tarea/)).toBeInTheDocument();
    expect(screen.queryByText(new RegExp(`${ANA_ID} completó`))).not.toBeInTheDocument();
  });

  it('la tarjeta "Ranking" del inicio también muestra el nombre del miembro, no su UUID', async () => {
    vi.stubGlobal("fetch", mockFetch(dashboardConDatos()));

    render(<InicioCasa casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText("Ana: 8 pts")).toBeInTheDocument();
    expect(screen.queryByText(`${ANA_ID}: 8 pts`)).not.toBeInTheDocument();
  });

  it("renderiza el banner de alerta con nombre y fecha para una tarjeta próxima a vencer (TC-008)", async () => {
    const dashboard = {
      ...dashboardVacio(),
      tarjetasConAlerta: [
        {
          id: "tj1",
          nombre: "Visa Platinum",
          banco: "BBVA",
          fecha_vencimiento_actual: "2026-09-07",
          dias_para_vencimiento: 6,
          vencida: false,
        },
      ],
    };
    vi.stubGlobal("fetch", mockFetch(dashboard));

    render(<InicioCasa casaId={CASA_ID} miembros={[]} />);

    const alerta = await screen.findByText(/Visa Platinum/);
    expect(alerta).toHaveTextContent("Visa Platinum");
    expect(alerta).toHaveTextContent("BBVA");
    expect(alerta).toHaveTextContent("2026-09-07");
    expect(alerta).toHaveTextContent("6");
    expect(alerta.closest('[role="alert"]')).not.toBeNull();
  });

  it("marca con severidad error el banner de una tarjeta ya vencida", async () => {
    const dashboard = {
      ...dashboardVacio(),
      tarjetasConAlerta: [
        {
          id: "tj2",
          nombre: "Mastercard Black",
          banco: "Galicia",
          fecha_vencimiento_actual: "2026-08-20",
          dias_para_vencimiento: -5,
          vencida: true,
        },
      ],
    };
    vi.stubGlobal("fetch", mockFetch(dashboard));

    render(<InicioCasa casaId={CASA_ID} miembros={[]} />);

    const texto = await screen.findByText(/Mastercard Black/);
    const alerta = texto.closest('[role="alert"]');
    expect(alerta).not.toBeNull();
    expect(alerta?.className).toMatch(/colorError|standardError/);
  });

  it("renderiza el banner de alerta de mantenimiento para un ítem próximo a vencer (TC-010)", async () => {
    const dashboard = {
      ...dashboardVacio(),
      mantenimientoConAlerta: [
        {
          id: "im1",
          nombre: "Poner membrana al techo",
          fecha_estimada: "2026-09-20",
          dias_para_vencimiento: 4,
          vencido: false,
        },
      ],
    };
    vi.stubGlobal("fetch", mockFetch(dashboard));

    render(<InicioCasa casaId={CASA_ID} miembros={[]} />);

    const alerta = await screen.findByText(/Poner membrana al techo/);
    expect(alerta).toHaveTextContent("2026-09-20");
    expect(alerta).toHaveTextContent("4");
    expect(alerta.closest('[role="alert"]')).not.toBeNull();
  });

  it("marca con severidad error el banner de un ítem de mantenimiento ya vencido", async () => {
    const dashboard = {
      ...dashboardVacio(),
      mantenimientoConAlerta: [
        {
          id: "im2",
          nombre: "Arreglar el reflector de la entrada",
          fecha_estimada: "2026-09-01",
          dias_para_vencimiento: -5,
          vencido: true,
        },
      ],
    };
    vi.stubGlobal("fetch", mockFetch(dashboard));

    render(<InicioCasa casaId={CASA_ID} miembros={[]} />);

    const texto = await screen.findByText(/Arreglar el reflector de la entrada/);
    const alerta = texto.closest('[role="alert"]');
    expect(alerta).not.toBeNull();
    expect(alerta?.className).toMatch(/colorError|standardError/);
  });

  it("no muestra ningún banner cuando tarjetasConAlerta está vacío", async () => {
    vi.stubGlobal("fetch", mockFetch(dashboardVacio()));

    render(<InicioCasa casaId={CASA_ID} miembros={[]} />);

    await screen.findByText("Todavía no hay gastos registrados.");
    expect(screen.queryAllByRole("alert")).toHaveLength(0);
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

    render(<InicioCasa casaId={CASA_ID} miembros={[]} />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/no existe/i);
  });
});
