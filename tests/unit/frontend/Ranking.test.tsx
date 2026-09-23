import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Ranking } from "../../../src/frontend/pages/Ranking";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ANA_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const DESCONOCIDO_ID = "ffffffff-ffff-ffff-ffff-ffffffffffff";

const MIEMBROS = [
  { id: ANA_ID, casa_id: CASA_ID, nombre: "Ana", identificacion: "ANA1", rol: "member", activo: true },
];

function mockFetch(ranking: unknown[], logros: unknown[] = []) {
  return vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes("/logros")) {
      return { ok: true, json: async () => logros };
    }
    if (url.includes("/ranking")) {
      return { ok: true, json: async () => ranking };
    }
    return { ok: true, json: async () => [] };
  });
}

describe("Ranking", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("muestra el nombre del miembro en vez del UUID (TC-001)", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch([{ miembroId: ANA_ID, puntos: 8, nivel: "Novato", racha: 0 }])
    );

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText("Ana")).toBeInTheDocument();
    expect(screen.queryByText(ANA_ID)).not.toBeInTheDocument();
  });

  it("usa el id crudo como fallback si el miembro no está en la lista recibida (TC-002)", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch([{ miembroId: DESCONOCIDO_ID, puntos: 3, nivel: "Novato", racha: 0 }])
    );

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText(DESCONOCIDO_ID)).toBeInTheDocument();
  });

  it("muestra un selector de mes, preseleccionado con el mes actual (TC-007)", async () => {
    vi.stubGlobal("fetch", mockFetch([]));

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    const selectorMes = await screen.findByLabelText("Mes");
    const mesActual = new Date().toISOString().slice(0, 7);
    expect(selectorMes).toHaveValue(mesActual);
  });

  it("cambiar el selector de mes vuelve a pedir el ranking con el mes elegido (TC-007)", async () => {
    const fetchMock = mockFetch([{ miembroId: ANA_ID, puntos: 8, nivel: "Novato", racha: 0 }]);
    vi.stubGlobal("fetch", fetchMock);

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);
    await screen.findByText("Ana");

    const user = userEvent.setup();
    const selectorMes = screen.getByLabelText("Mes");
    await user.clear(selectorMes);
    await user.type(selectorMes, "2026-08");

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(([input]) => String(input).includes("mes=2026-08"))
      ).toBe(true);
    });
  });

  it("muestra el nivel y la racha de cada miembro (TC-007)", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch([{ miembroId: ANA_ID, puntos: 60, nivel: "Activo", racha: 4 }])
    );

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    await screen.findByText("Ana");
    expect(screen.getByText("Activo")).toBeInTheDocument();
    expect(screen.getByText(/4 días/)).toBeInTheDocument();
  });

  it("muestra un indicador de progreso visual hacia el próximo nivel, no solo el número de puntos (TC-003)", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch([{ miembroId: ANA_ID, puntos: 60, nivel: "Activo", racha: 0 }])
    );

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    await screen.findByText("Ana");
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it('muestra 2 logros desbloqueados como chips/badges distintos entre sí, no como una lista separada por comas (TC-004)', async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch(
        [{ miembroId: ANA_ID, puntos: 8, nivel: "Novato", racha: 0 }],
        [
          {
            id: "l1",
            casa_id: CASA_ID,
            miembro_id: ANA_ID,
            logro_id: "primera_tarea",
            obtenido_en: "2026-09-01T10:00:00",
          },
          {
            id: "l2",
            casa_id: CASA_ID,
            miembro_id: ANA_ID,
            logro_id: "diez_tareas",
            obtenido_en: "2026-09-02T10:00:00",
          },
        ]
      )
    );

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    const chipPrimera = await screen.findByText("Primera tarea");
    const chipDiez = await screen.findByText("10 tareas completadas");
    expect(chipPrimera).toBeInTheDocument();
    expect(chipDiez).toBeInTheDocument();
    // Nunca una lista de texto separada por comas.
    expect(screen.queryByText("Primera tarea, 10 tareas completadas")).not.toBeInTheDocument();
  });

  it('muestra la sub-sección "Logros" con los logros desbloqueados de cada miembro (TC-007)', async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch(
        [{ miembroId: ANA_ID, puntos: 8, nivel: "Novato", racha: 1 }],
        [
          {
            id: "l1",
            casa_id: CASA_ID,
            miembro_id: ANA_ID,
            logro_id: "primera_tarea",
            obtenido_en: "2026-09-01T10:00:00",
          },
        ]
      )
    );

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText("Logros")).toBeInTheDocument();
    expect(await screen.findByText("Primera tarea")).toBeInTheDocument();
  });

  it('la sección "Logros" muestra un mensaje cuando todavía no hay ninguno desbloqueado', async () => {
    vi.stubGlobal("fetch", mockFetch([], []));

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText("Logros")).toBeInTheDocument();
    expect(screen.getByText("Todavía no se desbloqueó ningún logro.")).toBeInTheDocument();
  });
});
