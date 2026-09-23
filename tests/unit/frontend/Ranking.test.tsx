import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

// Spec `perfil-avatar-ui`: mismo criterio que `Miembros.test.tsx`/
// `LottieAvatar.test.tsx` — mockea `lottie-react` para que la fila con
// avatar seleccionado (TC-003) rendericé sin el efecto de red real.
vi.mock("lottie-react", () => ({
  Lottie: () => <div data-testid="lottie-mock" />,
}));

import { Ranking } from "../../../src/frontend/pages/Ranking";
import { crearFetchRouter, handlerAccesoriosEquipados, handlerAvatar } from "./helpers/mockFetchRouter";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ANA_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const DESCONOCIDO_ID = "ffffffff-ffff-ffff-ffff-ffffffffffff";

const MIEMBROS = [
  { id: ANA_ID, casa_id: CASA_ID, nombre: "Ana", identificacion: "ANA1", rol: "member", activo: true },
];

// Spec `perfil-avatar-ui`: desde esta spec cada fila también dispara sus
// propios fetches de avatar/accesorios equipados — `handlerAvatar()`/
// `handlerAccesoriosEquipados()` (por defecto `null`/`[]`) evitan que
// esas llamadas caigan en el `[]` genérico de respaldo de abajo, que es
// truthy como avatar y rompería TC-002/el resto de estos tests si no se
// interceptan antes.
function mockFetch(
  ranking: unknown[],
  logros: unknown[] = [],
  opciones: { avatares?: Record<string, unknown>; equipados?: Record<string, unknown[]> } = {}
) {
  return crearFetchRouter(
    [
      handlerAvatar(opciones.avatares),
      handlerAccesoriosEquipados(opciones.equipados),
      (url) => (url.includes("/logros") ? { ok: true, json: async () => logros } : undefined),
      (url) => (url.includes("/ranking") ? { ok: true, json: async () => ranking } : undefined),
    ],
    { ok: true, json: async () => [] }
  );
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

  it("TC-003 (avatar): una fila con avatar y accesorios equipados muestra LottieAvatar con los overlays", async () => {
    const avatarSeleccionado = {
      id: "avatar-1",
      especie: "gato",
      raza: "Siamés",
      lottie_url: "https://assets.lottiefiles.com/packages/lf20_siames.json",
      nivel_requerido: "Novato",
      rareza: "común",
    };
    const accesorioEquipado = {
      id: "accesorio-1",
      nombre: "Bufanda",
      slot: "cuello",
      rareza: "común",
      precio_creditos: 15,
      especie_compatible: "gato",
      asset_overlay_url: "https://assets.lottiefiles.com/packages/lf20_bufanda.json",
    };
    vi.stubGlobal(
      "fetch",
      mockFetch([{ miembroId: ANA_ID, puntos: 8, nivel: "Novato", racha: 0 }], [], {
        avatares: { [ANA_ID]: avatarSeleccionado },
        equipados: { [ANA_ID]: [accesorioEquipado] },
      })
    );

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    const fila = (await screen.findByText("Ana")).closest("tr")!;
    await waitFor(() => {
      expect(within(fila).getByTestId("lottie-mock")).toBeInTheDocument();
    });
    expect(within(fila).getByAltText("Bufanda")).toBeInTheDocument();
  });

  it("TC-002 (avatar): sin avatar seleccionado, la fila muestra el Avatar con inicial como respaldo", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch([{ miembroId: ANA_ID, puntos: 8, nivel: "Novato", racha: 0 }])
    );

    render(<Ranking casaId={CASA_ID} miembros={MIEMBROS} />);

    const fila = (await screen.findByText("Ana")).closest("tr")!;
    await waitFor(() => {
      expect(within(fila).getByLabelText("Avatar de Ana")).toBeInTheDocument();
    });
    expect(within(fila).queryByTestId("lottie-mock")).not.toBeInTheDocument();
  });
});
