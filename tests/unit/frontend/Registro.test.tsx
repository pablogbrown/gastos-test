import { ThemeProvider } from "@mui/material/styles";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Registro } from "../../../src/frontend/pages/Registro";
import { theme } from "../../../src/frontend/theme";

describe("Registro (TC-002)", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("el formulario está contenido en una tarjeta centrada con 'taskia' como encabezado (auth-onboarding TC-001)", () => {
    render(
      <ThemeProvider theme={theme}>
        <Registro onRegistroExitoso={vi.fn()} onIrALogin={vi.fn()} />
      </ThemeProvider>
    );

    const encabezado = screen.getByRole("heading", { name: "taskia" });
    expect(encabezado).toBeInTheDocument();
    expect(encabezado.closest(".MuiCard-root")).not.toBeNull();
  });

  it("un registro válido llama a POST /auth/registro y navega a Login", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: "u1", email: "ana@example.com" }),
    });
    vi.stubGlobal("fetch", fetchMock);
    const onRegistroExitoso = vi.fn();

    render(<Registro onRegistroExitoso={onRegistroExitoso} onIrALogin={vi.fn()} />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Ana");
    await user.type(screen.getByLabelText("Email"), "ana@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "unaClaveSegura");
    await user.click(screen.getByRole("button", { name: "Crear cuenta" }));

    await vi.waitFor(() => expect(onRegistroExitoso).toHaveBeenCalledTimes(1));

    expect(fetchMock).toHaveBeenCalledWith(
      "/auth/registro",
      expect.objectContaining({ method: "POST" })
    );
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(init.body as string)).toEqual({
      nombre: "Ana",
      email: "ana@example.com",
      password: "unaClaveSegura",
    });
  });

  it("muestra un error de email duplicado devuelto por la API (409)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 409,
        statusText: "Conflict",
        json: async () => ({ detail: "Ya existe un usuario registrado con el email 'ana@example.com'." }),
      })
    );

    render(<Registro onRegistroExitoso={vi.fn()} onIrALogin={vi.fn()} />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nombre"), "Ana");
    await user.type(screen.getByLabelText("Email"), "ana@example.com");
    await user.type(screen.getByLabelText("Contraseña"), "unaClaveSegura");
    await user.click(screen.getByRole("button", { name: "Crear cuenta" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/ya existe/i);
  });

  it("el link 'Iniciar sesión' vuelve a Login", async () => {
    const onIrALogin = vi.fn();
    render(<Registro onRegistroExitoso={vi.fn()} onIrALogin={onIrALogin} />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Iniciar sesión" }));

    expect(onIrALogin).toHaveBeenCalledTimes(1);
  });
});
