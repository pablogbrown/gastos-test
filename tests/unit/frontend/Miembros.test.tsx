import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Spec `perfil-avatar-ui`: `lottie-react`'s real `<Lottie src=.../>`
// fetchea/parsea la animación (efecto de red real) — se mockea acá,
// mismo criterio ya establecido por `LottieAvatar.test.tsx`, para que
// las tarjetas con avatar seleccionado (TC-001) rendericen sin ese
// efecto de red.
vi.mock("lottie-react", () => ({
  Lottie: () => <div data-testid="lottie-mock" />,
}));

import { Miembros } from "../../../src/frontend/pages/Miembros";
import {
  crearFetchRouter,
  handlerAccesoriosEquipados,
  handlerAvatar,
  handlerListaMiembros,
  respuestaError,
} from "./helpers/mockFetchRouter";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ADMIN_ID = "22222222-2222-2222-2222-222222222222";
const ANA_ID = "33333333-3333-3333-3333-333333333333";

const PENDIENTE_ID = "44444444-4444-4444-4444-444444444444";

const MIEMBROS_BASE = [
  {
    id: ADMIN_ID,
    usuario_id: ADMIN_ID,
    casa_id: CASA_ID,
    nombre: "Administrador",
    identificacion: ADMIN_ID,
    rol: "admin",
    activo: true,
  },
  {
    id: ANA_ID,
    usuario_id: ANA_ID,
    casa_id: CASA_ID,
    nombre: "Ana",
    identificacion: "ANA1",
    rol: "member",
    activo: true,
  },
];

const MIEMBROS_CON_PENDIENTE = [
  MIEMBROS_BASE[0],
  {
    id: PENDIENTE_ID,
    usuario_id: null,
    casa_id: CASA_ID,
    nombre: "Invitado Pendiente",
    identificacion: "PEND1",
    rol: "member",
    activo: true,
  },
];

// Spec `perfil-avatar-ui`: helpers de mock por URL/método en vez de por
// orden de invocación — desde esta spec, cada tarjeta de miembro
// dispara sus propios fetches de avatar/accesorios equipados,
// intercalados con el flujo principal de la pantalla (ver
// `helpers/mockFetchRouter.ts`).
function mockFetchListaMiembros(lista: unknown[] = MIEMBROS_BASE) {
  return crearFetchRouter([handlerListaMiembros([lista]), handlerAvatar(), handlerAccesoriosEquipados()]);
}

function mockFetchListaConMiembroPendiente() {
  return mockFetchListaMiembros(MIEMBROS_CON_PENDIENTE);
}

describe("Miembros", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", mockFetchListaMiembros());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("muestra el listado de miembros activos", async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    expect(await screen.findByText("Ana")).toBeInTheDocument();
    // "Administrador" aparece dos veces (nombre del fixture + chip de
    // rol, spec `pantallas-casa` REQ-001) — getAllByText en vez de
    // getByText porque ahora hay más de una coincidencia.
    expect(screen.getAllByText("Administrador").length).toBeGreaterThanOrEqual(1);
  });

  it("muestra cada miembro como tarjeta con avatar, nombre y chip de rol (TC-001)", async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    const tarjetaAdmin = await screen.findByRole("group", { name: "Miembro Administrador" });
    const tarjetaAna = screen.getByRole("group", { name: "Miembro Ana" });

    expect(within(tarjetaAdmin).getByLabelText("Avatar de Administrador")).toBeInTheDocument();
    expect(within(tarjetaAna).getByLabelText("Avatar de Ana")).toBeInTheDocument();

    // Chips de rol distintos entre sí (TC-001): un admin y un miembro
    // no deben mostrar la misma etiqueta de rol. "Administrador" aparece
    // dos veces en la tarjeta del admin (nombre + chip de rol, coincide
    // en este fixture) — se verifica la cantidad en vez de unicidad.
    expect(within(tarjetaAdmin).getAllByText("Administrador").length).toBeGreaterThanOrEqual(2);
    expect(within(tarjetaAna).getByText("Miembro")).toBeInTheDocument();
  });

  it("muestra la acción Desactivar para un Administrador", async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    await waitFor(() => expect(screen.getAllByText("Desactivar").length).toBeGreaterThan(0));
  });

  it("oculta la acción Desactivar y el alta para un rol Miembro (TC-006)", async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="member" />);

    await screen.findByText("Ana");
    expect(screen.queryByText("Desactivar")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Agregar miembro")).not.toBeInTheDocument();
  });

  it("muestra un error de identificación duplicada devuelto por la API (TC-004)", async () => {
    const fetchMock = crearFetchRouter([
      handlerListaMiembros([[]]),
      (url, init) => {
        if ((init?.method ?? "GET").toUpperCase() !== "POST" || !url.endsWith(`/casas/${CASA_ID}/miembros`)) {
          return undefined;
        }
        return respuestaError(400, "Ya existe un miembro con identificación 'ANA1'.", "Bad Request");
      },
      handlerAvatar(),
      handlerAccesoriosEquipados(),
    ]);
    vi.stubGlobal("fetch", fetchMock);

    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);
    await screen.findByLabelText("Agregar miembro");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Ana");
    await user.type(screen.getByLabelText("Identificación"), "ANA1");
    await user.type(screen.getByLabelText("Email"), "ana@example.com");
    await user.click(screen.getByRole("button", { name: "Agregar miembro" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/identificación/i);
  });

  it('muestra "Pendiente" y oculta Desactivar para una membresía sin usuario_id (TC-007)', async () => {
    vi.stubGlobal("fetch", mockFetchListaConMiembroPendiente());

    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    await screen.findByText("Invitado Pendiente");
    const filaPendiente = screen.getByRole("group", { name: "Miembro Invitado Pendiente" });

    expect(within(filaPendiente).getByText("Pendiente")).toBeInTheDocument();
    expect(within(filaPendiente).queryByText("Activo")).not.toBeInTheDocument();
    expect(within(filaPendiente).queryByText("Inactivo")).not.toBeInTheDocument();
    expect(within(filaPendiente).queryByText("Desactivar")).not.toBeInTheDocument();
  });

  it('sigue mostrando Activo/Inactivo y Desactivar para una membresía vinculada (TC-008)', async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    await screen.findByText("Ana");
    expect(screen.getAllByText("Activo").length).toBeGreaterThan(0);
    expect(screen.queryByText("Pendiente")).not.toBeInTheDocument();
    expect(screen.getAllByText("Desactivar").length).toBeGreaterThan(0);
  });

  it("envía el email del usuario a vincular al agregar un miembro (regresión: 'field required')", async () => {
    const fetchMock = crearFetchRouter([
      handlerListaMiembros([[]]),
      (url, init) => {
        if ((init?.method ?? "GET").toUpperCase() !== "POST" || !url.endsWith(`/casas/${CASA_ID}/miembros`)) {
          return undefined;
        }
        return {
          ok: true,
          json: async () => ({
            id: "55555555-5555-5555-5555-555555555555",
            casa_id: CASA_ID,
            nombre: "Pablo",
            identificacion: "papá",
            rol: "member",
            activo: true,
          }),
        };
      },
      handlerAvatar(),
      handlerAccesoriosEquipados(),
    ]);
    vi.stubGlobal("fetch", fetchMock);

    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);
    await screen.findByLabelText("Agregar miembro");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Pablo");
    await user.type(screen.getByLabelText("Identificación"), "papá");
    await user.type(screen.getByLabelText("Email"), "pablo@example.com");
    await user.click(screen.getByRole("button", { name: "Agregar miembro" }));

    // Spec `perfil-avatar-ui`: ya no se puede asumir que la llamada de
    // alta es `calls[1]` — cada tarjeta de miembro dispara sus propios
    // fetches de avatar intercalados (ver `mockFetchRouter.ts`) — se
    // busca la llamada POST por URL/método en vez de por índice.
    await waitFor(() => {
      const altaCall = fetchMock.mock.calls.find(
        ([input, init]) =>
          String(input).endsWith(`/casas/${CASA_ID}/miembros`) &&
          (init as RequestInit | undefined)?.method === "POST"
      );
      expect(altaCall).toBeDefined();
    });
    const altaCall = fetchMock.mock.calls.find(
      ([input, init]) =>
        String(input).endsWith(`/casas/${CASA_ID}/miembros`) &&
        (init as RequestInit | undefined)?.method === "POST"
    )!;
    const body = JSON.parse((altaCall[1] as RequestInit).body as string);
    expect(body).toEqual({ nombre: "Pablo", identificacion: "papá", email: "pablo@example.com" });
  });

  it("muestra el campo Meta de puntos mensual solo para un Administrador", async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);
    await screen.findByText("Ana");
    expect(screen.getByLabelText("Meta de puntos mensual")).toBeInTheDocument();
  });

  it("oculta el campo Meta de puntos mensual para un rol Miembro", async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="member" />);
    await screen.findByText("Ana");
    expect(screen.queryByLabelText("Meta de puntos mensual")).not.toBeInTheDocument();
  });

  it("guardar la meta llama a PATCH /casas/{id}/meta con el valor ingresado", async () => {
    const fetchMock = crearFetchRouter([
      handlerListaMiembros([MIEMBROS_BASE]),
      (url, init) => {
        if ((init?.method ?? "GET").toUpperCase() !== "PATCH" || !url.endsWith(`/casas/${CASA_ID}/meta`)) {
          return undefined;
        }
        return {
          ok: true,
          json: async () => ({
            id: CASA_ID,
            nombre: "Casa Brown",
            creado_en: "2026-01-01T00:00:00",
            miembros: [],
            meta_puntos_mensual: 150,
          }),
        };
      },
      handlerAvatar(),
      handlerAccesoriosEquipados(),
    ]);
    vi.stubGlobal("fetch", fetchMock);

    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);
    await screen.findByText("Ana");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Meta de puntos mensual"), "150");
    await user.click(screen.getByRole("button", { name: "Guardar meta" }));

    // Spec `perfil-avatar-ui`: se busca la llamada PATCH por URL/método
    // en vez de por índice — ver la misma nota en el test de alta.
    await waitFor(() => {
      const patchCall = fetchMock.mock.calls.find(
        ([input, init]) =>
          String(input).endsWith(`/casas/${CASA_ID}/meta`) && (init as RequestInit | undefined)?.method === "PATCH"
      );
      expect(patchCall).toBeDefined();
    });
    const patchCall = fetchMock.mock.calls.find(
      ([input, init]) =>
        String(input).endsWith(`/casas/${CASA_ID}/meta`) && (init as RequestInit | undefined)?.method === "PATCH"
    )!;
    expect((patchCall[1] as RequestInit).method).toBe("PATCH");
    const body = JSON.parse((patchCall[1] as RequestInit).body as string);
    expect(body).toEqual({ meta: 150 });

    expect(await screen.findByText(/Meta actualizada/)).toBeInTheDocument();
  });

  it("muestra un error devuelto por la API al guardar una meta inválida", async () => {
    const fetchMock = crearFetchRouter([
      (url, init) => {
        if ((init?.method ?? "GET").toUpperCase() !== "PATCH" || !url.endsWith(`/casas/${CASA_ID}/meta`)) {
          return undefined;
        }
        return respuestaError(400, "La meta de puntos debe ser un entero no negativo, o None.", "Bad Request");
      },
      handlerListaMiembros([MIEMBROS_BASE]),
      handlerAvatar(),
      handlerAccesoriosEquipados(),
    ]);
    vi.stubGlobal("fetch", fetchMock);

    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);
    await screen.findByText("Ana");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Meta de puntos mensual"), "-5");
    await user.click(screen.getByRole("button", { name: "Guardar meta" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/meta de puntos/i);
  });

  it("TC-001 (avatar): un miembro con avatar y accesorios equipados muestra LottieAvatar con los overlays, no el Avatar con inicial", async () => {
    const avatarSeleccionado = {
      id: "avatar-1",
      especie: "perro",
      raza: "Labrador",
      lottie_url: "https://assets.lottiefiles.com/packages/lf20_labrador.json",
      nivel_requerido: "Novato",
      rareza: "común",
    };
    const accesorioEquipado = {
      id: "accesorio-1",
      nombre: "Gorro de fiesta",
      slot: "cabeza",
      rareza: "común",
      precio_creditos: 10,
      especie_compatible: "perro",
      asset_overlay_url: "https://assets.lottiefiles.com/packages/lf20_gorro.json",
    };
    const fetchMock = crearFetchRouter([
      handlerListaMiembros([MIEMBROS_BASE]),
      handlerAvatar({ [ANA_ID]: avatarSeleccionado }),
      handlerAccesoriosEquipados({ [ANA_ID]: [accesorioEquipado] }),
    ]);
    vi.stubGlobal("fetch", fetchMock);

    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    const tarjetaAna = await screen.findByRole("group", { name: "Miembro Ana" });
    await waitFor(() => {
      expect(within(tarjetaAna).getByTestId("lottie-mock")).toBeInTheDocument();
    });
    expect(within(tarjetaAna).getByLabelText("Avatar de Ana")).toBeInTheDocument();
    expect(within(tarjetaAna).getByAltText("Gorro de fiesta")).toBeInTheDocument();

    // El admin (sin avatar en este fixture) sigue con el respaldo.
    const tarjetaAdmin = screen.getByRole("group", { name: "Miembro Administrador" });
    expect(within(tarjetaAdmin).getByText("A")).toBeInTheDocument();
  });

  it("TC-002 (avatar): un miembro sin avatar seleccionado sigue mostrando el Avatar con inicial como respaldo", async () => {
    render(<Miembros casaId={CASA_ID} rolUsuarioActual="admin" />);

    const tarjetaAna = await screen.findByRole("group", { name: "Miembro Ana" });
    await waitFor(() => {
      expect(within(tarjetaAna).getByText("A")).toBeInTheDocument();
    });
    expect(within(tarjetaAna).queryByTestId("lottie-mock")).not.toBeInTheDocument();
  });
});
