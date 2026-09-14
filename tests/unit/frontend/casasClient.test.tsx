import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { crearCasa, esApiError } from "../../../src/frontend/api/casasClient";

// Regresión: un 422 de FastAPI/Pydantic devuelve `detail` como un array
// de objetos {loc, msg, type}, no un string. El cliente debe convertirlo
// a un mensaje legible en vez de propagarlo tal cual — de lo contrario
// cualquier pantalla que renderiza `<Alert>{error.detail}</Alert>`
// crashea con "Objects are not valid as a React child".
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

  it("convierte un detail-array de Pydantic a un mensaje de texto legible", async () => {
    let caught: unknown;
    try {
      await crearCasa("");
    } catch (err) {
      caught = err;
    }

    expect(esApiError(caught)).toBe(true);
    if (esApiError(caught)) {
      expect(typeof caught.detail).toBe("string");
      expect(caught.detail).toContain("field required");
    }
  });
});
