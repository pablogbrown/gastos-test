import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AccesorioOverlayIcon } from "../../../src/frontend/components/AccesorioOverlayIcon";

/** Fix `avatar-assets-fallback`: mientras `asset_overlay_url` siga siendo
 * un placeholder no resoluble (deuda técnica documentada en
 * `avatares-economia`/`tienda-accesorios` [S001]/[S002]), la imagen rota
 * nativa del navegador (con el `alt` recortado encima) es un problema
 * visual real — este componente debe degradarse a un ícono prolijo. */
describe("AccesorioOverlayIcon", () => {
  it("muestra la imagen cuando carga correctamente", () => {
    render(<AccesorioOverlayIcon src="https://ejemplo.com/gorro.png" alt="Gorro de lana" />);

    const img = screen.getByAltText("Gorro de lana");
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("src", "https://ejemplo.com/gorro.png");
  });

  it("muestra un ícono de fallback en vez del ícono roto nativo cuando la imagen falla al cargar", () => {
    render(<AccesorioOverlayIcon src="https://ejemplo.com/roto.png" alt="Gorro de lana" />);

    const img = screen.getByAltText("Gorro de lana");
    fireEvent.error(img);

    expect(screen.queryByAltText("Gorro de lana")).not.toBeInTheDocument();
    expect(screen.getByTestId("accesorio-overlay-fallback")).toBeInTheDocument();
  });
});
