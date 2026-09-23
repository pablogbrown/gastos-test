import { useState } from "react";

import CheckroomIcon from "@mui/icons-material/Checkroom";
import Box from "@mui/material/Box";
import type { SxProps, Theme } from "@mui/material/styles";

export interface AccesorioOverlayIconProps {
  src: string;
  alt: string;
  size?: number | string;
  sx?: SxProps<Theme>;
}

/** Overlay de un accesorio (fix `avatar-assets-fallback`): mientras
 * `asset_overlay_url` siga siendo un placeholder no resoluble (deuda
 * técnica documentada en `avatares-economia`/`tienda-accesorios`
 * `[S001]`/`[S002]`), un `<img>` sin manejo de error muestra el ícono
 * roto nativo del navegador con el `alt` recortado encima — acá se
 * reemplaza por un ícono prolijo (`CheckroomIcon`) del mismo tamaño en
 * vez de eso, vía el `onError` estándar de `<img>`. Puramente
 * presentacional, mismo criterio ya establecido para `PageHeader`/
 * `StatCard`/`EmptyState`/`LottieAvatar` — sin imports de
 * `src/frontend/api/*`. */
export function AccesorioOverlayIcon({ src, alt, size = 40, sx }: AccesorioOverlayIconProps) {
  const [fallo, setFallo] = useState(false);

  if (fallo) {
    return (
      <Box
        data-testid="accesorio-overlay-fallback"
        aria-label={alt}
        sx={{
          width: size,
          height: size,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "action.disabled",
          ...sx,
        }}
      >
        <CheckroomIcon fontSize="inherit" sx={{ fontSize: typeof size === "number" ? size * 0.7 : "70%" }} />
      </Box>
    );
  }

  return (
    <Box
      component="img"
      src={src}
      alt={alt}
      onError={() => setFallo(true)}
      sx={{ width: size, height: size, ...sx }}
    />
  );
}
