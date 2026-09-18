import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Tareas } from "../../../src/frontend/pages/Tareas";

const CASA_ID = "11111111-1111-1111-1111-111111111111";
const ADMIN_ID = "22222222-2222-2222-2222-222222222222";
const ANA_ID = "33333333-3333-3333-3333-333333333333";
const BRUNO_ID = "44444444-4444-4444-4444-444444444444";

function miembroActivo(id: string, nombre: string) {
  return {
    id,
    casa_id: CASA_ID,
    nombre,
    identificacion: id,
    rol: "member",
    activo: true,
  };
}

function tareaSinResponsable() {
  return {
    id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    casa_id: CASA_ID,
    nombre: "Sacar la basura",
    descripcion: null,
    puntos: 5,
    responsableId: null,
    fechaPrevista: null,
    estado: "pendiente",
    recurrente: false,
    frecuencia: null,
  };
}

function tareaConResponsable(responsableId: string) {
  return {
    id: "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    casa_id: CASA_ID,
    nombre: "Pagar servicios",
    descripcion: null,
    puntos: 8,
    responsableId,
    fechaPrevista: null,
    estado: "pendiente",
    recurrente: false,
    frecuencia: null,
  };
}

/** Regresión (reportado en vivo): una tarea diaria no se debía poder
 * completar más seguido que su frecuencia. `fechaPrevista` en el futuro
 * ("mañana") reproduce la instancia recién generada por
 * `procesar_recurrencia` tras la primera finalización del día. */
function tareaRecurrenteConFecha(fechaPrevista: string) {
  return {
    id: "cccccccc-cccc-cccc-cccc-cccccccccccc",
    casa_id: CASA_ID,
    nombre: "Lavar los platos",
    descripcion: null,
    puntos: 1,
    responsableId: null,
    fechaPrevista,
    estado: "pendiente",
    recurrente: true,
    frecuencia: "diaria",
  };
}

function fechaManana(): string {
  const fecha = new Date();
  fecha.setDate(fecha.getDate() + 1);
  return fecha.toISOString().slice(0, 10);
}

function fechaHoy(): string {
  return new Date().toISOString().slice(0, 10);
}

function mockFetch(tareas: unknown[], historial: unknown[] = [], miembros: unknown[] = []) {
  return vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/historial")) {
      return { ok: true, json: async () => historial };
    }
    if (url.includes("/tareas")) {
      return { ok: true, json: async () => tareas };
    }
    if (url.includes("/miembros")) {
      return { ok: true, json: async () => miembros };
    }
    return { ok: true, json: async () => [] };
  });
}

describe("Tareas", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("muestra el listado de tareas y el historial", async () => {
    vi.stubGlobal("fetch", mockFetch([tareaSinResponsable()], []));

    render(<Tareas casaId={CASA_ID} miembroIdActual={ADMIN_ID} rolUsuarioActual="admin" />);

    expect(await screen.findByText("Sacar la basura")).toBeInTheDocument();
    expect(screen.getByText("Historial de tareas")).toBeInTheDocument();
  });

  it("el historial muestra el nombre del miembro y de la tarea, no sus UUID (reportado en vivo)", async () => {
    const tarea = tareaConResponsable(ANA_ID);
    const registroHistorial = {
      id: "dddddddd-dddd-dddd-dddd-dddddddddddd",
      casa_id: CASA_ID,
      tarea_id: tarea.id,
      miembro_id: ANA_ID,
      completada_en: "2026-09-16T17:55:54.867147",
      puntos_obtenidos: 8,
    };
    vi.stubGlobal(
      "fetch",
      mockFetch([tarea], [registroHistorial], [miembroActivo(ANA_ID, "Ana")])
    );

    render(<Tareas casaId={CASA_ID} miembroIdActual={ADMIN_ID} rolUsuarioActual="admin" />);

    const tablaHistorial = within(await screen.findByRole("table", { name: "Historial de tareas" }));
    expect(await tablaHistorial.findByText("Ana")).toBeInTheDocument();
    expect(tablaHistorial.getByText("Pagar servicios")).toBeInTheDocument();
    expect(tablaHistorial.queryByText(ANA_ID)).not.toBeInTheDocument();
    expect(tablaHistorial.queryByText(tarea.id)).not.toBeInTheDocument();
  });

  it("el historial muestra el uuid crudo como fallback si el miembro o la tarea ya no existen", async () => {
    const registroHistorial = {
      id: "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
      casa_id: CASA_ID,
      tarea_id: "ffffffff-ffff-ffff-ffff-ffffffffffff",
      miembro_id: "99999999-9999-9999-9999-999999999999",
      completada_en: "2026-09-16T17:55:54.867147",
      puntos_obtenidos: 3,
    };
    vi.stubGlobal("fetch", mockFetch([], [registroHistorial], []));

    render(<Tareas casaId={CASA_ID} miembroIdActual={ADMIN_ID} rolUsuarioActual="admin" />);

    expect(await screen.findByText("99999999-9999-9999-9999-999999999999")).toBeInTheDocument();
    expect(screen.getByText("ffffffff-ffff-ffff-ffff-ffffffffffff")).toBeInTheDocument();
  });

  it("muestra 'Marcar completada' para una tarea sin responsable a cualquier miembro", async () => {
    vi.stubGlobal("fetch", mockFetch([tareaSinResponsable()], []));

    render(<Tareas casaId={CASA_ID} miembroIdActual={ANA_ID} rolUsuarioActual="member" />);

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Marcar completada" })).toBeInTheDocument()
    );
  });

  it("oculta 'Marcar completada' si el miembro no es el responsable asignado (TC-004)", async () => {
    vi.stubGlobal("fetch", mockFetch([tareaConResponsable(ANA_ID)], []));

    render(<Tareas casaId={CASA_ID} miembroIdActual={BRUNO_ID} rolUsuarioActual="member" />);

    await screen.findByText("Pagar servicios");
    expect(screen.queryByRole("button", { name: "Marcar completada" })).not.toBeInTheDocument();
  });

  it("muestra 'Marcar completada' al propio responsable asignado", async () => {
    vi.stubGlobal("fetch", mockFetch([tareaConResponsable(ANA_ID)], []));

    render(<Tareas casaId={CASA_ID} miembroIdActual={ANA_ID} rolUsuarioActual="member" />);

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Marcar completada" })).toBeInTheDocument()
    );
  });

  it("oculta 'Marcar completada' en una tarea recurrente antes de su fecha prevista (regresión)", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch([tareaRecurrenteConFecha(fechaManana())], [])
    );

    render(<Tareas casaId={CASA_ID} miembroIdActual={ANA_ID} rolUsuarioActual="admin" />);

    await screen.findByText("Lavar los platos");
    expect(screen.queryByRole("button", { name: "Marcar completada" })).not.toBeInTheDocument();
  });

  it("muestra 'Marcar completada' en una tarea recurrente en su fecha prevista", async () => {
    vi.stubGlobal("fetch", mockFetch([tareaRecurrenteConFecha(fechaHoy())], []));

    render(<Tareas casaId={CASA_ID} miembroIdActual={ANA_ID} rolUsuarioActual="admin" />);

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Marcar completada" })).toBeInTheDocument()
    );
  });

  it("crea una tarea y refresca el listado", async () => {
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => tareaSinResponsable() })
      .mockResolvedValueOnce({ ok: true, json: async () => [tareaSinResponsable()] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] });
    vi.stubGlobal("fetch", fetchMock);

    render(<Tareas casaId={CASA_ID} miembroIdActual={ADMIN_ID} rolUsuarioActual="admin" />);
    await screen.findByLabelText("Crear tarea");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Sacar la basura");
    await user.type(screen.getByLabelText("Puntos"), "5");
    await user.click(screen.getByRole("button", { name: "Crear tarea" }));

    expect(await screen.findByText("Sacar la basura")).toBeInTheDocument();
  });

  it("muestra un error devuelto por la API al completar una tarea ya completada (TC-006)", async () => {
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: async () => [tareaSinResponsable()] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({
        ok: false,
        status: 409,
        statusText: "Conflict",
        json: async () => ({ detail: "La tarea ya fue completada." }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<Tareas casaId={CASA_ID} miembroIdActual={ANA_ID} rolUsuarioActual="member" />);
    await screen.findByText("Sacar la basura");

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Marcar completada" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/ya fue completada/i);
  });

  it("asigna el responsable de una tarea eligiendo un miembro existente (regresión: 'value is not a valid uuid')", async () => {
    const pablo = miembroActivo("55555555-5555-5555-5555-555555555555", "Pablo");
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [pablo] })
      .mockResolvedValueOnce({ ok: true, json: async () => tareaConResponsable(pablo.id) })
      .mockResolvedValueOnce({ ok: true, json: async () => [tareaConResponsable(pablo.id)] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [pablo] });
    vi.stubGlobal("fetch", fetchMock);

    render(<Tareas casaId={CASA_ID} miembroIdActual={ADMIN_ID} rolUsuarioActual="admin" />);
    await screen.findByLabelText("Crear tarea");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Barrer la casa");
    await user.type(screen.getByLabelText("Puntos"), "1");
    await user.selectOptions(screen.getByLabelText("Responsable (opcional)"), "Pablo");
    await user.click(screen.getByRole("button", { name: "Crear tarea" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(7));
    const [, crearRequest] = fetchMock.mock.calls[3];
    const body = JSON.parse((crearRequest as RequestInit).body as string);
    expect(body.responsableId).toBe(pablo.id);

    expect(await screen.findByText("Pagar servicios")).toBeInTheDocument();
    expect(await screen.findByRole("cell", { name: "Pablo" })).toBeInTheDocument();
  });

  it("muestra el error de negocio y no crea la tarea si Puntos queda vacío (TC-001)", async () => {
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        json: async () => ({
          detail: "La cantidad de puntos es obligatoria y debe ser un entero no negativo.",
        }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<Tareas casaId={CASA_ID} usuarioId={ADMIN_ID} rolUsuarioActual="admin" />);
    await screen.findByLabelText("Crear tarea");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Sacar la basura");
    await user.click(screen.getByRole("button", { name: "Crear tarea" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /cantidad de puntos es obligatoria/i
    );
    expect(screen.queryByText("Sacar la basura")).not.toBeInTheDocument();

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(4));
    const [, crearRequest] = fetchMock.mock.calls[3];
    const body = JSON.parse((crearRequest as RequestInit).body as string);
    expect(body).not.toHaveProperty("puntos");
  });

  it("sigue enviando puntos como número cuando el campo tiene valor (TC-002)", async () => {
    const fetchMock = vi.fn();
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => tareaSinResponsable() })
      .mockResolvedValueOnce({ ok: true, json: async () => [tareaSinResponsable()] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => [] });
    vi.stubGlobal("fetch", fetchMock);

    render(<Tareas casaId={CASA_ID} usuarioId={ADMIN_ID} rolUsuarioActual="admin" />);
    await screen.findByLabelText("Crear tarea");

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Sacar la basura");
    await user.type(screen.getByLabelText("Puntos"), "5");
    await user.click(screen.getByRole("button", { name: "Crear tarea" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(7));
    const [, crearRequest] = fetchMock.mock.calls[3];
    const body = JSON.parse((crearRequest as RequestInit).body as string);
    expect(body.puntos).toBe(5);

    expect(await screen.findByText("Sacar la basura")).toBeInTheDocument();
  });

  beforeEach(() => {
    vi.restoreAllMocks();
  });
});
