import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  TOKEN_STORAGE_KEY,
  cerrarSesion,
  fetchAutenticado,
  guardarSesion,
  obtenerToken,
  suscribirseACierreSesion,
} from "../../../src/frontend/api/authClient";

describe("authClient — sesión", () => {
  afterEach(() => {
    localStorage.clear();
    vi.unstubAllGlobals();
  });

  it("guardarSesion/obtenerToken persisten el JWT en localStorage", () => {
    expect(obtenerToken()).toBeNull();
    guardarSesion("un-jwt-cualquiera");
    expect(obtenerToken()).toBe("un-jwt-cualquiera");
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBe("un-jwt-cualquiera");
  });

  it("cerrarSesion borra el token guardado", () => {
    guardarSesion("un-jwt-cualquiera");
    cerrarSesion();
    expect(obtenerToken()).toBeNull();
  });

  it("cerrarSesion notifica a los suscriptores (REQ-005/TC-006)", () => {
    guardarSesion("un-jwt-cualquiera");
    const listener = vi.fn();
    const desuscribirse = suscribirseACierreSesion(listener);

    cerrarSesion();

    expect(listener).toHaveBeenCalledTimes(1);
    desuscribirse();
  });

  it("un suscriptor que se da de baja no vuelve a ser notificado", () => {
    guardarSesion("un-jwt-cualquiera");
    const listener = vi.fn();
    const desuscribirse = suscribirseACierreSesion(listener);
    desuscribirse();

    cerrarSesion();

    expect(listener).not.toHaveBeenCalled();
  });
});

describe("authClient — fetchAutenticado (TC-003, TC-004)", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
    vi.unstubAllGlobals();
  });

  it("TC-003: agrega Authorization: Bearer <jwt>, sin X-Usuario-Id, cuando hay sesión", async () => {
    guardarSesion("mi-jwt");
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({}) });
    vi.stubGlobal("fetch", fetchMock);

    await fetchAutenticado("/casas/x/miembros");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [, init] = fetchMock.mock.calls[0];
    const headers = init.headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer mi-jwt");
    expect(headers.get("X-Usuario-Id")).toBeNull();
  });

  it("no agrega Authorization si no hay sesión guardada", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({}) });
    vi.stubGlobal("fetch", fetchMock);

    await fetchAutenticado("/casas/x/miembros");

    const [, init] = fetchMock.mock.calls[0];
    const headers = init.headers as Headers;
    expect(headers.get("Authorization")).toBeNull();
  });

  it("TC-004: un 401 dispara cerrarSesion (logout automático)", async () => {
    guardarSesion("jwt-expirado");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 401, statusText: "Unauthorized" })
    );

    const listener = vi.fn();
    suscribirseACierreSesion(listener);

    await fetchAutenticado("/casas/x/miembros");

    expect(obtenerToken()).toBeNull();
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it("una respuesta que no es 401 no borra la sesión", async () => {
    guardarSesion("mi-jwt");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({}) }));

    await fetchAutenticado("/casas/x/miembros");

    expect(obtenerToken()).toBe("mi-jwt");
  });
});
