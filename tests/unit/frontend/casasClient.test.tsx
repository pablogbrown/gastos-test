import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { crearCasa, esApiError } from "../../../src/frontend/api/casasClient";

// Regresión: un 422 de FastAPI/Pydantic devuelve `detail` como un array
// de objetos {loc, msg, type}, no un string, con mensajes técnicos en
// inglés (ej. "field required"). El cliente debe convertirlo a un
// mensaje genérico amigable en vez de propagarlo tal cual — ni
// crashear (`<Alert>{error.detail}</Alert>` revienta con "Objects are
// not valid as a React child" si `detail` queda como array/objeto) ni
// mostrarle al usuario jerga de implementación.
describe("casasClient — manejo de error.detail no-string (422 de Pydantic)", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        statusText: "Unprocessable Entity",
        json: async () => ({
          detail: [
            { loc: ["body", "nombre"], msg: "field required", type: "value_error.missing" },
          ],
        }),
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("convierte un detail-array de Pydantic en un mensaje genérico amigable, sin jerga técnica", async () => {
    let caught: unknown;
    try {
      await crearCasa("");
    } catch (err) {
      caught = err;
    }

    expect(esApiError(caught)).toBe(true);
    if (esApiError(caught)) {
      expect(typeof caught.detail).toBe("string");
      expect(caught.detail).not.toContain("field required");
      expect(caught.detail).not.toMatch(/uuid|decimal|value_error/i);
      expect(caught.detail).toBe("Revisá que todos los campos estén completos y sean válidos.");
    }
  });
});
