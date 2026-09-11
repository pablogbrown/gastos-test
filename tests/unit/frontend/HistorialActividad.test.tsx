import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { HistorialActividad } from "../../../src/frontend/pages/HistorialActividad";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const USUARIO_ID = "22222222-2222-2222-2222-222222222222";

function mockFetch(actividad: unknown[]) {
  return vi.fn().mockResolvedValue({ ok: true, json: async () => actividad });
}

describe("HistorialActividad", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("muestra un mensaje vacío cuando la casa no tiene actividad registrada", async () => {
    vi.stubGlobal("fetch", mockFetch([]));

    render(<HistorialActividad casaId={CASA_ID} usuarioId={USUARIO_ID} />);

    expect(
      await screen.findByText("Todavía no hay actividad registrada.")
    ).toBeInTheDocument();
  });

  it("lista las entradas de actividad en el orden recibido, más reciente primero (TC-005)", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch([
        {
          id: "e2",
          casa_id: CASA_ID,
          tipo: "tarea_completada",
          miembro_id: "ana",
          fecha: "2026-01-02T10:00:00",
          descripcion: "Ana completó la tarea 'Lavar los platos'.",
        },
        {
          id: "e1",
          casa_id: CASA_ID,
          tipo: "gasto_registrado",
          miembro_id: "ana",
          fecha: "2026-01-01T10:00:00",
          descripcion: "Ana registró un gasto de $10000.",
        },
      ])
    );

    render(<HistorialActividad casaId={CASA_ID} usuarioId={USUARIO_ID} />);

    const items = await screen.findAllByRole("listitem");
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveTextContent("Ana completó la tarea 'Lavar los platos'.");
    expect(items[1]).toHaveTextContent("Ana registró un gasto de $10000.");
  });
});
