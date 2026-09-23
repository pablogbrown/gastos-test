import { ThemeProvider } from "@mui/material/styles";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatCard } from "../../../src/frontend/components/StatCard";
import { theme } from "../../../src/frontend/theme";

function conTema(children: React.ReactElement) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}

describe("StatCard (TC-005)", () => {
  it("TC-005: label y value son visibles, y value usa tipografía de mayor peso/tamaño que label", () => {
    render(conTema(<StatCard label="Total" value="$50.000" />));

    const valueEl = screen.getByText("$50.000");
    const labelEl = screen.getByText("Total");
    expect(valueEl).toBeInTheDocument();
    expect(labelEl).toBeInTheDocument();

    const valueStyle = getComputedStyle(valueEl);
    const labelStyle = getComputedStyle(labelEl);

    const valueWeight = parseInt(valueStyle.fontWeight || "400", 10);
    const labelWeight = parseInt(labelStyle.fontWeight || "400", 10);
    const valueSize = parseFloat(valueStyle.fontSize || "0");
    const labelSize = parseFloat(labelStyle.fontSize || "0");

    expect(valueWeight > labelWeight || valueSize > labelSize).toBe(true);
  });

  it("con color semántico aplica el color correspondiente del tema al value", () => {
    render(conTema(<StatCard label="Vencidos" value="3" color="error" />));
    const valueEl = screen.getByText("3");
    expect(getComputedStyle(valueEl).color).not.toBe("");
  });
});
