import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

// Spec `perfil-avatar-ui`: mismo criterio ya establecido por
// `LottieAvatar.test.tsx`/`Miembros.test.tsx` — se mockea `lottie-react`
// para que esta pantalla (2 avatares Lottie: el actual + cada raza de la
// sección "Razas") rendericé sin el efecto de red real.
vi.mock("lottie-react", () => ({
  Lottie: () => <div data-testid="lottie-mock" />,
}));

import { MiAvatar } from "../../../src/frontend/pages/MiAvatar";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const MIEMBRO_ID = "22222222-2222-2222-2222-222222222222";

const LABRADOR = {
  id: "avatar-labrador",
  especie: "perro",
  raza: "Labrador",
  lottie_url: "https://assets.lottiefiles.com/packages/lf20_labrador.json",
  nivel_requerido: "Novato",
  rareza: "común",
};
const BULLDOG = {
  id: "avatar-bulldog",
  especie: "perro",
  raza: "Bulldog",
  lottie_url: "https://assets.lottiefiles.com/packages/lf20_bulldog.json",
  nivel_requerido: "Novato",
  rareza: "común",
};
const PASTOR_ALEMAN = {
  id: "avatar-pastor",
  especie: "perro",
  raza: "Pastor Alemán",
  lottie_url: "https://assets.lottiefiles.com/packages/lf20_pastor.json",
  nivel_requerido: "Activo",
  rareza: "raro",
};

const GORRO = {
  id: "accesorio-gorro",
  nombre: "Gorro de fiesta",
  slot: "cabeza",
  rareza: "común",
  precio_creditos: 15,
  especie_compatible: "perro",
  asset_overlay_url: "https://assets.lottiefiles.com/packages/lf20_gorro.json",
};

interface EstadoBackend {
  saldo: number;
  avatarActual: typeof LABRADOR | null;
  inventario: (typeof GORRO)[];
  equipados: (typeof GORRO)[];
}

/** Fake de backend con estado mutable — más robusto que un mock por
 * índice/orden de invocación para esta pantalla: cada acción del usuario
 * (elegir raza, comprar, equipar) dispara SU PROPIA llamada de
 * confirmación (`GET /avatar`, `GET /creditos`) además de la mutación —
 * el estado compartido asegura que ambas reflejen el mismo resultado sin
 * depender de qué llamada ocurre en qué posición. */
function mockBackend(estadoInicial: Partial<EstadoBackend> = {}) {
  const estado: EstadoBackend = {
    saldo: 40,
    avatarActual: LABRADOR,
    inventario: [],
    equipados: [],
    ...estadoInicial,
  };

  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const metodo = (init?.method ?? "GET").toUpperCase();

    if (metodo === "GET" && url.endsWith("/creditos")) {
      return { ok: true, json: async () => ({ saldo: estado.saldo }) };
    }
    if (metodo === "GET" && url.endsWith("/avatares-disponibles")) {
      return { ok: true, json: async () => [LABRADOR, BULLDOG] };
    }
    if (metodo === "GET" && url.endsWith("/avatares-catalogo")) {
      return { ok: true, json: async () => [LABRADOR, BULLDOG, PASTOR_ALEMAN] };
    }
    if (metodo === "GET" && url.endsWith("/avatar")) {
      return { ok: true, json: async () => estado.avatarActual };
    }
    if (metodo === "PUT" && url.endsWith("/avatar")) {
      const body = JSON.parse((init!.body as string) ?? "{}");
      const nuevo = [LABRADOR, BULLDOG].find((raza) => raza.id === body.avatar_personaje_id) ?? null;
      estado.avatarActual = nuevo;
      return { ok: true, json: async () => nuevo };
    }
    if (metodo === "GET" && url.endsWith("/accesorios/catalogo")) {
      return { ok: true, json: async () => [GORRO] };
    }
    if (metodo === "GET" && url.endsWith("/accesorios/equipados")) {
      return { ok: true, json: async () => estado.equipados };
    }
    if (metodo === "GET" && url.endsWith("/accesorios")) {
      return { ok: true, json: async () => estado.inventario };
    }
    if (metodo === "POST" && url.endsWith("/comprar")) {
      estado.saldo -= GORRO.precio_creditos;
      estado.inventario = [...estado.inventario, GORRO];
      return { ok: true, json: async () => GORRO };
    }
    if (metodo === "PUT" && url.endsWith("/accesorios/equipar")) {
      estado.equipados = [GORRO];
      return { ok: true, json: async () => GORRO };
    }
    return { ok: true, json: async () => null };
  });

  return { fetchMock, estado };
}

describe("MiAvatar", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("TC-004: muestra las razas desbloqueadas como seleccionables y las bloqueadas con el nivel requerido visible", async () => {
    const { fetchMock } = mockBackend();
    vi.stubGlobal("fetch", fetchMock);

    render(<MiAvatar casaId={CASA_ID} miembroId={MIEMBRO_ID} />);

    const tarjetaLabrador = await screen.findByRole("button", { name: "Elegir raza Labrador" });
    expect(within(tarjetaLabrador).getByText("Activa")).toBeInTheDocument();

    const tarjetaBulldog = screen.getByRole("button", { name: "Elegir raza Bulldog" });
    expect(within(tarjetaBulldog).queryByText("Activa")).not.toBeInTheDocument();

    // Bloqueada: nunca un botón seleccionable, y su nivel requerido a la vista.
    expect(screen.queryByRole("button", { name: "Elegir raza Pastor Alemán" })).not.toBeInTheDocument();
    expect(screen.getByText("Pastor Alemán")).toBeInTheDocument();
    expect(screen.getByText("Nivel Activo")).toBeInTheDocument();
  });

  it("TC-005: seleccionar una raza desbloqueada llama a seleccionarAvatar y la pantalla refleja el nuevo avatar activo", async () => {
    const { fetchMock } = mockBackend();
    vi.stubGlobal("fetch", fetchMock);

    render(<MiAvatar casaId={CASA_ID} miembroId={MIEMBRO_ID} />);
    await screen.findByRole("button", { name: "Elegir raza Labrador" });

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Elegir raza Bulldog" }));

    await waitFor(() => {
      const putAvatar = fetchMock.mock.calls.find(
        ([input, init]) => String(input).endsWith("/avatar") && (init as RequestInit | undefined)?.method === "PUT"
      );
      expect(putAvatar).toBeDefined();
    });
    const putAvatar = fetchMock.mock.calls.find(
      ([input, init]) => String(input).endsWith("/avatar") && (init as RequestInit | undefined)?.method === "PUT"
    )!;
    const body = JSON.parse((putAvatar[1] as RequestInit).body as string);
    expect(body).toEqual({ avatar_personaje_id: BULLDOG.id });

    await waitFor(() => {
      expect(within(screen.getByRole("button", { name: "Elegir raza Bulldog" })).getByText("Activa")).toBeInTheDocument();
    });
    expect(
      within(screen.getByRole("button", { name: "Elegir raza Labrador" })).queryByText("Activa")
    ).not.toBeInTheDocument();
  });

  it("TC-006: comprar y equipar un accesorio actualiza el saldo mostrado y lo deja equipado, sin recargar la pantalla", async () => {
    const { fetchMock } = mockBackend();
    vi.stubGlobal("fetch", fetchMock);

    render(<MiAvatar casaId={CASA_ID} miembroId={MIEMBRO_ID} />);
    expect(await screen.findByText("40")).toBeInTheDocument();

    const user = userEvent.setup();
    await user.click(await screen.findByRole("button", { name: "Comprar" }));

    // Saldo baja el precio del accesorio, sin ningún reload de la pantalla.
    await waitFor(() => expect(screen.getByText("25")).toBeInTheDocument());

    const botonEquipar = await screen.findByRole("button", { name: "Equipar" });
    await user.click(botonEquipar);

    await waitFor(() => expect(screen.getByText("Equipado")).toBeInTheDocument());
    expect(screen.queryByRole("button", { name: "Equipar" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Comprar" })).not.toBeInTheDocument();
  });

  it("muestra un error devuelto por la API al intentar comprar sin saldo suficiente", async () => {
    const { fetchMock, estado } = mockBackend({ saldo: 5 });
    fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const metodo = (init?.method ?? "GET").toUpperCase();
      if (metodo === "POST" && url.endsWith("/comprar")) {
        return { ok: false, status: 402, statusText: "Payment Required", json: async () => ({ detail: "Saldo insuficiente." }) };
      }
      if (metodo === "GET" && url.endsWith("/creditos")) return { ok: true, json: async () => ({ saldo: estado.saldo }) };
      if (metodo === "GET" && url.endsWith("/avatares-disponibles")) return { ok: true, json: async () => [LABRADOR] };
      if (metodo === "GET" && url.endsWith("/avatares-catalogo")) return { ok: true, json: async () => [LABRADOR] };
      if (metodo === "GET" && url.endsWith("/avatar")) return { ok: true, json: async () => LABRADOR };
      if (metodo === "GET" && url.endsWith("/accesorios/catalogo")) return { ok: true, json: async () => [GORRO] };
      if (metodo === "GET" && (url.endsWith("/accesorios/equipados") || url.endsWith("/accesorios"))) {
        return { ok: true, json: async () => [] };
      }
      return { ok: true, json: async () => null };
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<MiAvatar casaId={CASA_ID} miembroId={MIEMBRO_ID} />);

    const user = userEvent.setup();
    await user.click(await screen.findByRole("button", { name: "Comprar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/saldo/i);
  });
});
