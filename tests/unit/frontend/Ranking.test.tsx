import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Ranking } from "../../../src/frontend/pages/Ranking";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ANA_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const DESCONOCIDO_ID = "ffffffff-ffff-ffff-ffff-ffffffffffff";

const MIEMBROS = [
  { id: ANA_ID, casa_id: CASA_ID, nombre: "Ana", identificacion: "ANA1", rol: "member", activo: true },
];

function mockFetch(ranking: unknown) {
  return vi.fn().mockResolvedValue({ ok: true, json: async () => ranking });
}

describe("Ranking", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("muestra el nombre del miembro en vez del UUID (TC-001)", async () => {
    vi.stubGlobal("fetch", mockFetch([{ miembroId: ANA_ID, puntos: 8 }]));

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText("Ana")).toBeInTheDocument();
    expect(screen.queryByText(ANA_ID)).not.toBeInTheDocument();
  });

  it("usa el id crudo como fallback si el miembro no está en la lista recibida (TC-002)", async () => {
    vi.stubGlobal("fetch", mockFetch([{ miembroId: DESCONOCIDO_ID, puntos: 3 }]));

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    expect(await screen.findByText(DESCONOCIDO_ID)).toBeInTheDocument();
  });
});
