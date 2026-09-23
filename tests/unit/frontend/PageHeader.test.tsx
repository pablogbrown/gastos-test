import { ThemeProvider } from "@mui/material/styles";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PageHeader } from "../../../src/frontend/components/PageHeader";
import { theme } from "../../../src/frontend/theme";

function conTema(children: React.ReactElement) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}

describe("PageHeader (TC-003)", () => {
  it("TC-003: el título es visible por rol de heading y la acción dispara onClick al hacer click", () => {
    const onClick = vi.fn();
    render(conTema(<PageHeader title="Gastos" action={{ label: "Nuevo", onClick }} />));

    expect(screen.getByRole("heading", { name: "Gastos" })).toBeInTheDocument();

    const boton = screen.getByRole("button", { name: "Nuevo" });
    fireEvent.click(boton);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("sin action no muestra ningún botón", () => {
    render(conTema(<PageHeader title="Inicio" />));

    expect(screen.getByRole("heading", { name: "Inicio" })).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("con subtitle lo muestra junto al título", () => {
    render(conTema(<PageHeader title="Gastos" subtitle="Casa de prueba" />));

    expect(screen.getByText("Casa de prueba")).toBeInTheDocument();
  });
});
