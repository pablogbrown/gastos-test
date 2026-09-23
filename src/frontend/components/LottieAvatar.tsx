import PetsIcon from "@mui/icons-material/Pets";
import Box from "@mui/material/Box";
import { Lottie } from "lottie-react";

export interface LottieAvatarProps {
  src: string;
  loop?: boolean;
  className?: string;
}

/** Reproductor Lottie compartido (spec `avatares-economia`, REQ-005):
 * reproduce la animación de una raza a partir de su `lottie_url`
 * (URL o path de texto plano), sin conocer nada de la lógica de negocio
 * de avatares/créditos — puramente presentacional, mismo criterio ya
 * establecido para `PageHeader`/`StatCard`/`EmptyState`
 * (`rediseno-ux-ui/sistema-visual`). Nunca importa nada de
 * `src/frontend/api/*` (constraint de la spec).
 *
 * `lottie-react`'s `<Lottie src=.../>` acepta tanto una URL/path (la
 * fetchea y parsea sola) como un objeto de animación ya parseado —
 * cubre las dos formas que puede tener `AvatarPersonaje.lottie_url` sin
 * que este componente tenga que decidir entre fetch/import él mismo.
 *
 * Fix `avatar-assets-fallback`: `lottie-react` v3.1.2 no expone ningún
 * prop de error/fallback en `<Lottie>` (verificado contra su código
 * fuente publicado — `LottieError`/`useLottie` existen pero como piezas
 * de composición manual, no como una opción de `<Lottie>` mismo), y
 * duplicar el fetch acá mismo para detectar la falla introduciría una
 * segunda llamada de red además de complicar cada test que renderiza
 * este componente con un mock de `fetch` global. En cambio, se renderiza
 * SIEMPRE un ícono de fallback (`PetsIcon`) detrás del reproductor: si
 * la animación carga, la cubre visualmente (el lienzo de `lottie-react`
 * es opaco sobre su sujeto); si `lottie_url` es un placeholder no
 * resoluble (deuda técnica documentada en `avatares-economia`
 * `[S001]`), el ícono queda visible en vez de un cuadro en blanco. Sin
 * detección de error, sin red adicional, sin mocks nuevos en ningún test
 * existente. */
export function LottieAvatar({ src, loop = true, className }: LottieAvatarProps) {
  return (
    <Box className={className} sx={{ position: "relative", width: "100%", height: "100%" }}>
      <Box
        data-testid="lottie-avatar-fallback"
        aria-hidden="true"
        sx={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "action.disabled",
        }}
      >
        <PetsIcon fontSize="inherit" sx={{ fontSize: "70%" }} />
      </Box>
      <Box sx={{ position: "relative", width: "100%", height: "100%" }}>
        <Lottie src={src} loop={loop} autoplay />
      </Box>
    </Box>
  );
}
