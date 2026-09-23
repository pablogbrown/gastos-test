import { ThemeProvider } from "@mui/material/styles";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { EmptyState } from "../../../src/frontend/components/EmptyState";
import { theme } from "../../../src/frontend/theme";

function conTema(children: React.ReactElement) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}

describe("EmptyState (TC-004)", () => {
  it("TC-004: sin action muestra el ícono y el mensaje, sin ningún botón", () => {
    const { container } = render(conTema(<EmptyState message="Sin gastos todavía" />));

    expect(screen.getByText("Sin gastos todavía")).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(container.querySelector('[data-testid="empty-state-icon"], svg')).not.toBeNull();
  });

  it("con action muestra un botón que dispara onClick", () => {
    const onClick = vi.fn();
    render(
      conTema(
        <EmptyState message="Sin datos" action={{ label: "Agregar el primero", onClick }} />
      )
    );

    const boton = screen.getByRole("button", { name: "Agregar el primero" });
    fireEvent.click(boton);
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
