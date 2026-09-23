import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// `lottie-react`'s real `<Lottie src=.../>` fetchea/parsea la animación
// (efecto de red real) — se mockea acá para un test unitario puro, mismo
// criterio que cualquier otro componente de este proyecto que envuelve
// una librería externa con efectos propios. Se captura la prop `src`
// recibida para verificar TC-009 sin depender de una URL real.
const LottieMock = vi.fn(() => <div data-testid="lottie-mock" />);
vi.mock("lottie-react", () => ({
  Lottie: (props: { src: string }) => LottieMock(props),
}));

import { LottieAvatar } from "../../../src/frontend/components/LottieAvatar";

describe("LottieAvatar (TC-009)", () => {
  it("TC-009: el reproductor Lottie subyacente recibe la URL como fuente de animación", () => {
    const url = "https://assets.lottiefiles.com/packages/lf20_ejemplo.json";
    render(<LottieAvatar src={url} />);

    expect(LottieMock).toHaveBeenCalledTimes(1);
    expect(LottieMock.mock.calls[0][0]).toMatchObject({ src: url });
  });

  it("por defecto reproduce en loop", () => {
    render(<LottieAvatar src="https://assets.lottiefiles.com/packages/lf20_otro.json" />);
    expect(LottieMock.mock.calls.at(-1)?.[0]).toMatchObject({ loop: true });
  });

  it("loop={false} se pasa tal cual al reproductor subyacente", () => {
    render(
      <LottieAvatar src="https://assets.lottiefiles.com/packages/lf20_otro.json" loop={false} />
    );
    expect(LottieMock.mock.calls.at(-1)?.[0]).toMatchObject({ loop: false });
  });

  it("fix avatar-assets-fallback: siempre renderiza un ícono de fallback debajo del reproductor, visible mientras la animación no cubra el cuadro (ej. lottie_url placeholder no resoluble)", () => {
    render(<LottieAvatar src="https://assets.lottiefiles.com/packages/lf20_placeholder_no_existe.json" />);

    expect(screen.getByTestId("lottie-avatar-fallback")).toBeInTheDocument();
  });
});
