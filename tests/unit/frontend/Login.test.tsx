import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { TOKEN_STORAGE_KEY } from "../../../src/frontend/api/authClient";
import { Login } from "../../../src/frontend/pages/Login";

describe("Login (TC-001, TC-003)", () => {
  afterEach(() => {
    localStorage.clear();
    vi.unstubAllGlobals();
  });

  it("sin JWT guardado se muestra el formulario de Login, no el shell (TC-001)", () => {
    render(<Login onLoginExitoso={vi.fn()} onIrARegistro={vi.fn()} />);

    expect(screen.getByLabelText("Iniciar sesión")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Ingresar" })).toBeInTheDocument();
  });

  it("un login exitoso guarda el JWT y notifica onLoginExitoso", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ access_token: "un-jwt-valido", token_type: "bearer" }),
      })
    );
    const onLoginExitoso = vi.fn();

    render(<Login onLoginExitoso={onLoginExitoso} onIrARegistro={vi.fn()} />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Email"), "ana@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "unaClaveSegura");
    await user.click(screen.getByRole("button", { name: "Ingresar" }));

    await vi.waitFor(() => expect(onLoginExitoso).toHaveBeenCalledTimes(1));
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBe("un-jwt-valido");
  });

  it("muestra el error devuelto por la API ante credenciales inválidas", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: "Unauthorized",
        json: async () => ({ detail: "Email o contraseña incorrectos." }),
      })
    );

    render(<Login onLoginExitoso={vi.fn()} onIrARegistro={vi.fn()} />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Email"), "ana@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "incorrecta");
    await user.click(screen.getByRole("button", { name: "Ingresar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/incorrectos/i);
  });

  it("el link 'Registrate' navega a Registro", async () => {
    const onIrARegistro = vi.fn();
    render(<Login onLoginExitoso={vi.fn()} onIrARegistro={onIrARegistro} />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Registrate" }));

    expect(onIrARegistro).toHaveBeenCalledTimes(1);
  });
});
